# -*- encoding: utf-8 -*-
from odoo import fields, api, models, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
import requests
import json
import datetime

import logging
log = logging.getLogger(__name__)


class LogisticDespatch(models.Model):
    _inherit = 'logistic.despatch'

    @api.model
    def get_l10n_pe_dte_shipment_reason(self):
        lst = []
        lst.append(("01", "Venta"))
        lst.append(("02", "Compra"))
        lst.append(("04", "Traslado entre establecimientos de la misma empresa"))
        lst.append(("08", "Importacion"))
        lst.append(("09", "Exportacion"))
        lst.append(("13", "Otros"))
        lst.append(("14", "Venta sujeta a confirmación del comprador"))
        lst.append(("18", "Traslado emisor itinerante CP"))
        lst.append(("19", "Traslado a zona primaria"))
        return lst

    @api.model
    def get_l10n_pe_dte_transport_mode(self):
        lst = []
        lst.append(("01", "Transporte publico"))
        lst.append(("02", "Transporte privado"))
        return lst

    l10n_latam_country_code = fields.Char("Country Code (LATAM)",
        related='company_id.country_id.code', help='Technical field used to hide/show fields regarding the localization')
    l10n_pe_dte_shipment_reason = fields.Selection('get_l10n_pe_dte_shipment_reason', string='Reason', required=True, readonly=True, states={
                                       'draft': [('readonly', False)], }, default='01')
    l10n_pe_dte_transport_mode = fields.Selection('get_l10n_pe_dte_transport_mode', string='Mode', required=True, readonly=True, states={
                                      'draft': [('readonly', False)], }, default='02')
    l10n_pe_dte_status = fields.Selection([
        ('not_sent', 'Pending To Be Sent'),
        ('ask_for_status', 'Ask For Status'),
        ('accepted', 'Accepted'),
        ('objected', 'Accepted With Objections'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
        ('manual', 'Manual'),
    ], default='not_sent', string='SUNAT DTE status', copy=False, tracking=True, help="""Status of sending the DTE to the SUNAT:
    - Not sent: the DTE has not been sent to SUNAT but it has created.
    - Ask For Status: The DTE is asking for its status to the SUNAT.
    - Accepted: The DTE has been accepted by SUNAT.
    - Accepted With Objections: The DTE has been accepted with objections by SUNAT.
    - Rejected: The DTE has been rejected by SUNAT.
    - Manual: The DTE is sent manually, i.e.: the DTE will not be sending manually.""")
    l10n_pe_dte_void_status = fields.Selection([
        ('not_sent', 'Pending To Be Sent'),
        ('ask_for_status', 'Ask For Status'),
        ('accepted', 'Accepted'),
        ('objected', 'Accepted With Objections'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
        ('manual', 'Manual'),
    ], string='SUNAT DTE Void status', copy=False, tracking=True, help="""Status of sending the Void DTE to the SUNAT:
    - Not sent: the DTE has not been sent to SUNAT but it has created.
    - Ask For Status: The DTE is asking for its status to the SUNAT.
    - Accepted: The DTE has been accepted by SUNAT.
    - Accepted With Objections: The DTE has been accepted with objections by SUNAT.
    - Rejected: The DTE has been rejected by SUNAT.
    - Manual: The DTE is sent manually, i.e.: the DTE will not be sending manually.""")
    l10n_pe_dte_cancel_reason = fields.Char(
        string="Cancel Reason", copy=False,
        help="Reason given by the user to cancel this move")
    l10n_pe_dte_partner_status = fields.Selection([
        ('not_sent', 'Not Sent'),
        ('sent', 'Sent'),
    ], string='Partner DTE status', copy=False, help="""
    Status of sending the DTE to the partner:
    - Not sent: the DTE has not been sent to the partner but it has sent to SII.
    - Sent: The DTE has been sent to the partner.""")
    l10n_pe_dte_file = fields.Many2one('ir.attachment', string='DTE file', copy=False)
    l10n_pe_dte_file_link = fields.Char(string='DTE file', compute='_compute_l10n_pe_dte_links')
    l10n_pe_dte_hash = fields.Char(string='DTE Hash', copy=False)
    l10n_pe_dte_pdf_file = fields.Many2one('ir.attachment', string='DTE PDF file', copy=False)
    l10n_pe_dte_pdf_file_link = fields.Char(string='DTE PDF file', compute='_compute_l10n_pe_dte_links')
    l10n_pe_dte_cdr_file = fields.Many2one('ir.attachment', string='CDR file', copy=False)
    l10n_pe_dte_cdr_file_link = fields.Char(string='CDR file', compute='_compute_l10n_pe_dte_links')
    l10n_pe_dte_cdr_void_file = fields.Many2one('ir.attachment', string='CDR Void file', copy=False)
    l10n_pe_dte_cdr_void_file_link = fields.Char(string='CDR Void file', compute='_compute_l10n_pe_dte_links')
    l10n_pe_dte_invoice_number = fields.Char(string='Numero de Factura')
    l10n_pe_dte_is_einvoice = fields.Boolean('Is E-invoice')

    def _compute_l10n_pe_dte_links(self):
        for move in self:
            move.l10n_pe_dte_file_link = move.l10n_pe_dte_file.url if move.l10n_pe_dte_file else None
            move.l10n_pe_dte_pdf_file_link = move.l10n_pe_dte_pdf_file.url if move.l10n_pe_dte_pdf_file else None
            move.l10n_pe_dte_cdr_file_link = move.l10n_pe_dte_cdr_file.url if move.l10n_pe_dte_cdr_file else None
            move.l10n_pe_dte_cdr_void_file_link = move.l10n_pe_dte_cdr_void_file.url if move.l10n_pe_dte_cdr_void_file else None

    def action_open(self):
        res = super(LogisticDespatch, self).action_open()
        for move in self:
            if move.journal_id.l10n_pe_is_dte:
                if not self.origin_address_id.zip:
                    raise ValidationError("El ubigeo de la direccion de partida es obligatorio")
                if not self.delivery_address_id.zip:
                    raise ValidationError("El ubigeo de la direccion de llegada es obligatorio")
                move.l10n_pe_dte_is_einvoice = True
            if move.l10n_pe_dte_is_einvoice and move.company_id.l10n_pe_dte_send_interval_unit=="immediately":
                move.l10n_pe_dte_action_send()
        return res
    
    def l10n_pe_dte_action_send(self):
        #override this method for custom integration
        pass

    def l10n_pe_dte_action_check(self):
        #override this method for custom integration
        pass

    def l10n_pe_dte_action_cancel(self):
        #override this method for custom integration
        pass
    
    def _l10n_pe_prepare_dte(self):
        sequence = self.name.split('-')
        serial = sequence[0]
        number = sequence[1]

        _despatch = {
            'enviar': True,
            'serie': serial,
            'numero': number,
            'nombre_de_archivo': '%s-09-%s' % (self.company_id.vat,self.name),
            'motivo_de_envio': self.l10n_pe_dte_shipment_reason,
            'modo_de_transporte': self.l10n_pe_dte_transport_mode,
            'tipo_de_guia': '09',
            'informacion_de_envio': self.l10n_pe_dte_shipment_reason,

            'receptor_denominacion': self.partner_id.name,
            'receptor_tipo_de_documento': self.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code,
            'receptor_numero_de_documento': self.partner_id.vat,
            'receptor_direccion': self.partner_id.street,
            'fecha_de_emision': self.issue_date.strftime("%Y-%m-%d"),
            'fecha_de_inicio': self.start_date.strftime("%Y-%m-%d"),

            'peso': self.total_weight,
            'unidad_de_medida_peso': 'KGM',
            'bultos_paquetes': self.packages,

            'origen_ubigeo': self.origin_address_id.zip.replace('PE', '') if self.origin_address_id.zip else False,
            #'origen_direccion': self.origin_address_id.street,
            'origen_direccion': (self.origin_address_id.street_name or '') \
                                + (self.origin_address_id.street_number and (' ' + self.origin_address_id.street_number) or '') \
                                + (self.origin_address_id.street_number2 and (' ' + self.origin_address_id.street_number2) or '') \
                                + (self.origin_address_id.street2 and (' ' + self.origin_address_id.street2) or '') \
                                + (self.origin_address_id.l10n_pe_district and ', ' + self.origin_address_id.l10n_pe_district.name or '') \
                                + (self.origin_address_id.city_id and ', ' + self.origin_address_id.city_id.name or '') \
                                + (self.origin_address_id.state_id and ', ' + self.origin_address_id.state_id.name or '') \
                                + (self.origin_address_id.country_id and ', ' + self.origin_address_id.country_id.name or ''),
            'destino_ubigeo': self.delivery_address_id.zip.replace('PE', '') if self.delivery_address_id.zip else False,
            #'destino_direccion': self.delivery_address_id.street ,
            'destino_direccion': (self.delivery_address_id.street_name or '') \
                                + (self.delivery_address_id.street_number and (' ' + self.delivery_address_id.street_number) or '') \
                                + (self.delivery_address_id.street_number2 and (' ' + self.delivery_address_id.street_number2) or '') \
                                + (self.delivery_address_id.street2 and (' ' + self.delivery_address_id.street2) or '') \
                                + (self.delivery_address_id.l10n_pe_district and ', ' + self.delivery_address_id.l10n_pe_district.name or '') \
                                + (self.delivery_address_id.city_id and ', ' + self.delivery_address_id.city_id.name or '') \
                                + (self.delivery_address_id.state_id and ', ' + self.delivery_address_id.state_id.name or '') \
                                + (self.delivery_address_id.country_id and ', ' + self.delivery_address_id.country_id.name or ''),
            #'observaciones': self.note,
            'items': []
        }
        if self.l10n_pe_dte_invoice_number:
            _despatch['numero_de_factura_referencia'] = self.l10n_pe_dte_invoice_number
        if self.note:
            if self.note!='':
                _despatch['observaciones'] = self.note
        if self.vehicle_id:
            _despatch.update({
                'placa_de_vehiculo': self.vehicle_id.license_plate,
            })
        if self.driver_id:
            _despatch.update({
                'placa_de_vehiculo': self.vehicle_id.license_plate,
                'operador_denominacion': self.driver_id.name,
                'operador_tipo_de_documento': self.driver_id.l10n_latam_identification_type_id.l10n_pe_vat_code,
                'operador_numero_de_documeto': self.driver_id.vat,
                'operador_licencia': self.driver_id.logistic_license_number,
            })
        if self.carrier_id:
            _despatch.update({
                'portador_denominacion': self.carrier_id.name,
                'portador_tipo_de_documento': self.carrier_id.l10n_latam_identification_type_id.l10n_pe_vat_code,
                'portador_numero_de_documento': self.carrier_id.vat
            })

        if self.line_ids:
            for line in self.line_ids:
                _item = {
                    'cantidad': line.quantity,
                    'descripcion': line.name.replace('[%s] ' % line.product_id.default_code,'') if line.product_id else line.name,
                    'codigo': line.product_id.default_code or '',
                    'codigo_producto_sunat': line.product_id.l10n_pe_edi_unspsc or '',
                    'unidad_de_medida': line.product_id.uom_id.l10n_pe_edi_unece or 'NIU',
                    'peso': line.weight,
                    'unidad_de_medida_peso': self.weight_uom.l10n_pe_edi_unece or 'KGM',
                }
                if _item.get('codigo') == None:
                    _item['codigo'] = ''
                _despatch['items'].append(_item)
        log.info(_despatch)
        return _despatch

    def verify_partner_company(self):
        if self.l10n_pe_dte_shipment_reason == '01' and self.partner_id and self.journal_id.l10n_pe_is_dte:
            if self.partner_id.id == self.company_id.partner_id.id:
                raise ValidationError(
                    "El remitente no puede ser igual al destinatario")

    def verify_address_street(self, address_street):
        new_address = address_street
        new_address = new_address.translate(
            {ord(c): " " for c in "°!@#$%^&*()[]{};:,./<>?\|`~-=_+'"})
        new_address = new_address.strip()
        count_newaddress = len(new_address)
        if count_newaddress > 0:
            if new_address[0] == '\n':
                new_address[0] = ''
            if new_address[count_newaddress-1] == '\n':
                new_address[count_newaddress-1] = ''
        new_address = new_address.replace("ñ", "n")
        new_address = new_address.replace("Ñ", "N")
        new_address = new_address.replace("á", "a")
        new_address = new_address.replace("Á", "A")
        new_address = new_address.replace("é", "e")
        new_address = new_address.replace("É", "E")
        new_address = new_address.replace("í", "i")
        new_address = new_address.replace("Í", "I")
        new_address = new_address.replace("ó", "o")
        new_address = new_address.replace("Ó", "O")
        new_address = new_address.replace("ú", "u")
        new_address = new_address.replace("Ú", "U")
        if len(new_address) > 100:
            new_address = new_address[:100]
        return new_address

    def _get_name_despatch_report(self, report_xml_id):
        self.ensure_one()
        if self.company_id.country_id.code == 'PE':
            custom_report = {
                'logistic.report_despatch_document': 'l10n_pe_edi_extended_despatch.report_despatch_document',
            }
            return custom_report.get(report_xml_id) or report_xml_id
        return super()._get_name_despatch_report(report_xml_id)

    def action_despatch_sent(self):
        """ Open a window to compose an email, with the edi despatch template
            message loaded by default
        """
        res = super(LogisticDespatch, self).action_despatch_sent()
        template = self.env.ref('l10n_pe_edi_extended_despatch.email_template_edi_despatch', raise_if_not_found=False)
        if template:
            res['context'].update({'default_template_id': template and template.id or False})
        return res