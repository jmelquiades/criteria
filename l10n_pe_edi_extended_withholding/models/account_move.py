# -*- coding: utf-8 -*-
from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError
import json
import logging
log = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "account.move"

    l10n_pe_dte_withholding_type = fields.Selection([
        ('01', 'Tasa 3%'),
        ('02', 'Tasa 6%'),
    ], string='IGV Retention Type', copy=True, readonly=True,
        states={'draft': [('readonly', False)]},)

    def _get_l10n_latam_documents_domain(self):
        res = super(AccountMove, self)._get_l10n_latam_documents_domain()
        self.ensure_one()
        if self.is_withholding_receipt:
            res = [('code', '=', '20'), ('country_id', '=', self.company_id.account_fiscal_country_id.id)]
        return res

    def l10n_pe_dte_action_send(self):
        super(AccountMove, self).l10n_pe_dte_action_send()
        ir_attach = self.env['ir.attachment']
        for move in self.filtered(
                lambda x: x.company_id.country_id.code == "PE" and
                            x.company_id.l10n_pe_dte_service_provider in ['CONFLUX'] and 
                            x.journal_id.l10n_pe_is_dte):
            if move.is_withholding_receipt and move.journal_id.type == 'general' and not move.l10n_pe_dte_conflux_uid:
                data_dict = move._l10n_pe_prepare_dte_withholding_conflux()
                log.info(data_dict)
                response = self._send_json_to_conflux(ws_url='https://einvoice.conflux.pe/api/v/1/account_einvoice/retention/',token=move.company_id.l10n_pe_dte_conflux_token, data_dict=data_dict)
                if response[0]:
                    if response[1].get("status")=="success":
                        xml_attach = ir_attach.create({
                            "name":"%s.xml" % data_dict.get('nombre_de_archivo'),
                            'res_model': self._name,
                            'res_id': self.id,
                            "type":'url',
                            "url":response[1]["success"]["data"].get("enlace_del_xml")
                        })
                        pdf_attach = ir_attach.create({
                            "name":"%s.pdf" % data_dict.get('nombre_de_archivo'),
                            'res_model': self._name,
                            'res_id': self.id,
                            "type":'url',
                            "url":response[1]["success"]["data"].get("enlace_del_pdf")
                        })

                        _invoice = {
                            "l10n_pe_dte_file":xml_attach.id,
                            "l10n_pe_dte_pdf_file":pdf_attach.id,
                            "l10n_pe_dte_hash":response[1]["success"]["data"].get("codigo_hash"),
                            "l10n_pe_dte_status":'ask_for_status',
                            "l10n_pe_dte_partner_status":'not_sent',
                            "l10n_pe_dte_conflux_uid": response[1]["success"]["data"].get("uid"),
                        }

                        has_sunat_notes = False
                        if response[1]["success"]["data"].get('sunat_note', False) and response[1]["success"]["data"].get('sunat_note', False)!="":
                            has_sunat_notes = True
                            _invoice.update({
                                "l10n_pe_dte_status": 'objected',
                            })

                        if response[1]["success"]["data"].get("enlace_del_cdr") and response[1]["success"]["data"].get("emision_aceptada", False):
                            cdr_attach = ir_attach.create({
                                "name":"R-%s.xml" % data_dict.get('nombre_de_archivo'),
                                'res_model': self._name,
                                'res_id': self.id,
                                "type":'url',
                                "url":response[1]["success"]["data"].get("enlace_del_cdr")
                            })
                            _invoice.update({
                                "l10n_pe_dte_cdr_file":cdr_attach.id,
                                "l10n_pe_dte_status_response": '%s - %s' % (response[1]["success"]["data"].get('sunat_description', ''), response[1]["success"]["data"].get('sunat_note', '')) if has_sunat_notes else '',
                                "l10n_pe_dte_status":"accepted",
                            })

                        move.write(_invoice)
                    else:
                        if 'El comprobante fue previamente comunicado hacia nuestros servicios' in response[1]['error']['message']:
                            log.info('comprobante existe en portal de proveedor %s', self.name)
                            #TODO: Verficacion API REST de comprobante en portal de proveedor
                        raise ValidationError('%s\n\nInformacion tecnica:\n\n %s' % (response[1]["error"]["message"], json.dumps(response[1]["error"])))
                else:
                    raise UserError(response[1])

    def _l10n_pe_prepare_dte_withholding_conflux(self):
        dte_serial = ''
        dte_number = ''
        if self.l10n_latam_use_documents and self.l10n_latam_document_number:
            seq_split = self.l10n_latam_document_number.split('-')
            if len(seq_split)==2:
                dte_serial = seq_split[0]
                dte_number = seq_split[1]
        else:
            seq_split = self.name.split('-')
            if len(seq_split)==2:
                dte_serial = seq_split[0]
                dte_number = seq_split[1]

        conflux_dte = {
            'enviar': True,
            'proveedor_denominacion': self.partner_id.commercial_partner_id.name or self.partner_id.commercial_partner_id.name,
            'proveedor_tipo_de_documento': self.partner_id.vat,
            'proveedor_numero_de_documento': self.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code,
            'proveedor_direccion': (self.partner_id.street_name or '') \
                                + (self.partner_id.street_number and (' ' + self.partner_id.street_number) or '') \
                                + (self.partner_id.street_number2 and (' ' + self.partner_id.street_number2) or '') \
                                + (self.partner_id.street2 and (' ' + self.partner_id.street2) or '') \
                                + (self.partner_id.l10n_pe_district and ', ' + self.partner_id.l10n_pe_district.name or '') \
                                + (self.partner_id.city_id and ', ' + self.partner_id.city_id.name or '') \
                                + (self.partner_id.state_id and ', ' + self.partner_id.state_id.name or '') \
                                + (self.partner_id.country_id and ', ' + self.partner_id.country_id.name or ''),
            'serie': dte_serial,
            'numero': dte_number,
            'moneda': 'PEN',
            'fecha_de_emision': self.withholding_date.strftime('%Y-%m-%d'),
            'tipo_de_tasa_de_retencion': self.l10n_pe_dte_withholding_type,
            'total_retenido':0,
            'total_pagado':0,
            'observaciones':self.narration or '',
            'items':[]
        }
        for line in self.withholding_line_ids:
            sequence = line.invoice_id.ref.split('-')
            conflux_dte['items'].append({
                "documento_relacionado_tipo": line.invoice_id.l10n_latam_document_type_id.code,
                "documento_relacionado_serie": sequence[0],
                "documento_relacionado_numero": sequence[1],
                "documento_relacionado_fecha_de_emision": line.invoice_id.invoice_date.strftime('%Y-%m-%d'),
                "documento_relacionado_moneda": line.invoice_id.currency_id.name,
                "documento_relacionado_total": abs(line.invoice_id.amount_total), #EN MONEDA DEL COMPROBANTE
                "pago_fecha": line.l10n_pe_dte_payment_date.strftime('%Y-%m-%d'),
                "pago_numero": line.l10n_pe_dte_payment_number,
                "pago_total_sin_retencion": line.amount_base if line.invoice_id.currency_id==line.move_id.currency_id else line.amount_base/line.l10n_pe_dte_currency_rate, #EN MONEDA DEL COMPROBANTE
                "tipo_de_cambio": line.l10n_pe_dte_currency_rate,
                "tipo_de_cambio_fecha": line.l10n_pe_dte_currency_rate_date.strftime('%Y-%m-%d'),
                "importe_retenido": abs(line.amount), #EN SOLES
                "importe_retenido_fecha": line.l10n_pe_dte_withholding_date.strftime('%Y-%m-%d'),
                "importe_pagado_con_retencion": line.amount_base-line.amount, #EN SOLES
            })
            conflux_dte['total_retenido']+=abs(line.amount)
            conflux_dte['total_pagado']+=line.amount_base-line.amount
        return conflux_dte

class AccountMoveWithholdingLine(models.Model):
    _inherit = "account.move.withholding.line"

    l10n_pe_dte_payment_date = fields.Date(string='Fecha de pago')
    l10n_pe_dte_payment_number = fields.Selection([('1','Primer o unico pago'),('2','Segundo Pago'),('3','Terce Pago')], default='1', string='Numero de pago')
    #l10n_pe_dte_payment_total = fields.Float(string='Pago sin Retentcion')
    l10n_pe_dte_currency_rate = fields.Float(string='T.C.')
    l10n_pe_dte_currency_rate_date = fields.Date(string='Fecha del T.C.')
    l10n_pe_dte_withholding_date = fields.Date(string='Fecha de Retención')

    def _recompute_from_invoice_id(self):
        super(AccountMoveWithholdingLine, self)._recompute_from_invoice_id()
        self.ensure_one()
        self.l10n_pe_dte_payment_date = self.invoice_id.invoice_date
        #self.l10n_pe_dte_payment_total = self.invoice_id.amount_total
        self.l10n_pe_dte_currency_rate = abs(self.invoice_id.amount_total_signed/self.invoice_id.amount_total) if abs(self.invoice_id.amount_total)>0 else 1
        self.l10n_pe_dte_currency_rate_date = self.l10n_pe_dte_payment_date
        self.l10n_pe_dte_withholding_date = self.l10n_pe_dte_payment_date

    @api.onchange('l10n_pe_dte_payment_date')
    def _onchange_l10n_pe_dte_payment_date(self):
        self.l10n_pe_dte_withholding_date = self.l10n_pe_dte_payment_date