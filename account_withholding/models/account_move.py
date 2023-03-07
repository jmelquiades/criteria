# -*- coding: utf-8 -*-
from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError
import json
import logging
log = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "account.move"

    is_withholding_receipt = fields.Boolean(string='Is Withholding receipt?')
    withholding_date = fields.Date(string='Withholding Date')
    withholding_line_ids = fields.One2many('account.move.withholding.line','move_id')

    @api.onchange('withholding_line_ids')
    def _onchange_withholding_line_ids(self):
        log.info('_onchange_withholding_line_ids*********************')
        log.info(self)
        self._recompute_withholding_dynamic_lines()

    def _recompute_withholding_dynamic_lines(self):
        self.ensure_one()
        in_draft_mode = self != self._origin
        #self.line_ids.unlink()
        for withholding_line in self.withholding_line_ids:
            amount_currency = withholding_line.amount
            if withholding_line.tax_id:
                tax_move_line_vals = {
                    'name':withholding_line.invoice_id.ref,
                    'account_id': withholding_line.account_id.id,
                    'credit': withholding_line.amount > 0.0 and withholding_line.amount or 0.0,
                    'debit': withholding_line.amount < 0.0 and -withholding_line.amount or 0.0,
                    'quantity': 1.0,
                    'amount_currency': amount_currency,
                    #'partner_id': self.partner_id.id,
                    'move_id': self.id,
                    'currency_id': self.currency_id.id,
                    'company_id': self.company_id.id,
                    'company_currency_id': self.company_id.currency_id.id,
                    'exclude_from_invoice_tab': True,
                    'withholding_line_id':withholding_line._origin.id
                }
            invoice_payable_line = withholding_line.invoice_id.line_ids.filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
            if invoice_payable_line:
                invoice_move_line_vals = {
                    'name':withholding_line.invoice_id.ref,
                    'account_id': invoice_payable_line[0].account_id.id,
                    'debit': withholding_line.amount > 0.0 and withholding_line.amount or 0.0,
                    'credit': withholding_line.amount < 0.0 and -withholding_line.amount or 0.0,
                    'quantity': 1.0,
                    'amount_currency': invoice_payable_line[0].amount_currency,
                    'partner_id': invoice_payable_line[0].partner_id.id,
                    'move_id': self.id,
                    'currency_id': self.currency_id.id,
                    'company_id': self.company_id.id,
                    'company_currency_id': self.company_id.currency_id.id,
                    'exclude_from_invoice_tab': True,
                    'withholding_line_id':withholding_line._origin.id
                }

            existing_move_lines = self.line_ids.filtered(lambda line: line.withholding_line_id==withholding_line._origin)
            invoice_move_line = existing_move_lines.filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
            tax_move_line = existing_move_lines-invoice_move_line

            create_move_lines = []

            if invoice_payable_line:
                if invoice_move_line:
                    invoice_move_line.update({
                        'amount_currency': invoice_move_line_vals['amount_currency'],
                        'debit': invoice_move_line_vals['debit'],
                        'credit': invoice_move_line_vals['credit'],
                        'account_id': invoice_move_line_vals['account_id'],
                    })
                else:
                    create_move_lines.append(invoice_move_line_vals)

            if withholding_line.tax_id:
                if tax_move_line:
                    tax_move_line.update({
                        'amount_currency': tax_move_line_vals['amount_currency'],
                        'debit': tax_move_line_vals['debit'],
                        'credit': tax_move_line_vals['credit'],
                        'account_id': tax_move_line_vals['account_id'],
                    })
                else:
                    create_move_lines.append(tax_move_line_vals)
            
            if len(create_move_lines)>0:
                create_method = in_draft_mode and self.env['account.move.line'].new or self.env['account.move.line'].create
                log.info(create_move_lines)
                #create_method(create_move_lines)
                for create in create_move_lines:
                    create_method(create)

    '''def _get_retention_taxes(self):
        lines = {}
        for line in self.invoice_line_ids:
            ret_taxes_ids = line.tax_ids.filtered(lambda r: r.tax_group_id.name == 'RET')
            if ret_taxes_ids:
                taxes_discount = line.tax_ids.compute_all(line.price_unit * (1 - (line.discount or 0.0) / 100.0), self.currency_id, line.quantity, product=line.product_id, partner=self.partner_id, is_refund=self.move_type in ('out_refund', 'in_refund'))
                retention_details = [r for r in taxes_discount['taxes'] if r['id'] in ret_taxes_ids.ids]
                log.info(retention_details)
                for retention_detail in retention_details:
                    if not lines.get(retention_detail['id'], False):
                        lines[retention_detail['id']] = {
                            'id':retention_detail['id'],
                            'name':retention_detail['name'],
                            'account_id':retention_detail['account_id'],
                            'base':0,
                            'amount':0
                        }
                    lines[retention_detail['id']]['base']+=retention_detail['base']
                    lines[retention_detail['id']]['amount']+=retention_detail['amount']
        return lines.values()'''

    '''def _prepare_retention_lines(self):
        data = []
        retention_taxes = self._get_retention_taxes()
        for retention_tax in retention_taxes:
            data.append({
                #'tax_ids':[6,6,self.],
                'invoice_id':self.id,
                'account_id':retention_tax['account_id'],
                'amount_base':abs(retention_tax['base']),
                'amount_retention':abs(retention_tax['amount'])
            })
        return data

    def _prepare_retention(self):
        data = {
            'partner_id':self.partner_id.id,
            'move_type':'entry',
            'is_retention_receipt':True,
            'retention_line_ids': [ (0,0,i) for i in self._prepare_retention_lines()]
        }
        return data

    def action_generate_retention(self):
        self.ensure_one()
        amount_retention = sum([x[2] for x in self.amount_by_group2 if x[0] == 'RET'])
        if amount_retention==0:
            raise UserError(_('Invoice does not contains retention taxes'))
        retention = self.env['account.move'].create(self._prepare_retention())
        retention._onchange_retention_line_ids()
        compose_form = self.env.ref('account.view_move_form', raise_if_not_found=False)
        return {
            'name': _('Retention Receipt'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': retention.id,
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'current',
            'context': {
                'default_move_type':'entry',
                'default_is_retention_receipt': True
            },
        }'''

    def l10n_pe_dte_action_send(self):
        super(AccountMove, self).l10n_pe_dte_action_send()
        ir_attach = self.env['ir.attachment']
        for move in self.filtered(
                lambda x: x.company_id.country_id.code == "PE" and
                            x.company_id.l10n_pe_dte_service_provider in ['CONFLUX'] and 
                            x.journal_id.l10n_pe_is_dte):
            # generation of customer invoices
            if move.is_withholding_receipt and move.journal_id.type == 'general' and not move.l10n_pe_dte_conflux_uid:
                #move._l10n_cl_edi_post_validation()
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
            'fecha_de_emision': self.invoice_date.strftime('%Y-%m-%d'),
            'regimen_de_retencion': self.l10n_pe_dte_retention_type,
            'tasa_de_retencion': 3 if self.l10n_pe_dte_retention_type=='01' else 6 if self.l10n_pe_dte_retention_type=='03' else 0,
            'total_retenido':
            'total_pagado'
            'observaciones'
        }
        return conflux_dte

class AccountMoveWithholdingLine(models.Model):
    _name = "account.move.withholding.line"

    move_id = fields.Many2one('account.move', string='Account Move')
    #tax_id = fields.Many2one('account.tax', string='Tax')
    tax_id = fields.Many2one('account.tax', string='Tax')
    invoice_id = fields.Many2one('account.move', string='Invoice')
    account_id = fields.Many2one('account.account', string='Account')
    amount_base = fields.Float(string='Amount Base')
    amount = fields.Float(string='Amount')

    @api.onchange('tax_id')
    def _onchange_tax_id(self):
        if self.tax_id:
            self.account_id = self.tax_id.invoice_repartition_line_ids.filtered(lambda r:r.repartition_type=='tax').account_id

    @api.onchange('invoice_id')
    def _onchange_invoice_id(self):
        self._recompute_from_invoice_id()

    def _recompute_from_invoice_id(self):
        self.ensure_one()
        if self.invoice_id:
            self.amount_base = abs(self.invoice_id.amount_total_signed) if self.invoice_id.move_type=='in_invoice' else -abs(self.invoice_id.amount_total_signed)

    @api.onchange('amount_base')
    def _onchange_amount_base(self):
        for line in self:
            line.update(self._get_withholding_amount_totals())

    def _get_withholding_amount_totals(self):
        self.ensure_one()
        return self._get_withholding_amount_totals_model(amount_base=self.amount_base,taxes=self.tax_id)

    def _get_withholding_amount_totals_model(self, amount_base, taxes):
        res = {}
        amount_tax = 0
        if taxes:
            taxes_res = taxes._origin.with_context(force_sign=1).compute_all(amount_base,
                quantity=1, currency=None, product=None, partner=None)
            #res['amount'] = taxes_res['total_excluded']
            res['amount'] = abs(sum([tax['amount'] for tax in taxes_res['taxes']]))
        else:
            res['amount'] = amount_tax
        return res

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    withholding_line_id = fields.Many2one('account.move.withholding.line', string='Withholding Line')