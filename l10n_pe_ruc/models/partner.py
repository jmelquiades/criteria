# -*- coding: utf-8 -*-

from lxml import etree
from odoo import api, models, fields
from odoo.exceptions import Warning
from .apps import SunatPartnerConflux
import json
import logging


class ActivityEconomicSunat(models.Model):
    _name = 'activity.economic.sunat'
    _description = 'Actividad(es) Económica(s) SUNAT'
    name = fields.Char(
        string='Nombre',
        required=True
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Socio'
    )


class DocumentPaySunat(models.Model):
    _name = 'document.pay.sunat'
    _description = 'Comprobantes de Pago c/aut. de impresión (F. 806 u 816) - SUNAT'

    name = fields.Char(
        string='Nombre',
        required=True
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Socio'
    )


class SystemElectronicSunat(models.Model):
    _name = 'system.electronic.sunat'
    _description = 'Sistema de Emision Electronica - SUNAT'

    name = fields.Char(
        string='Nombre',
        required=True
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Socio'
    )


class PatternSunat(models.Model):
    _name = 'pattern.sunat'
    _description = 'Padrones - SUNAT'

    name = fields.Char(
        string='Nombre',
        required=True
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Socio'
    )


class ResPartner(models.Model):
    _inherit = 'res.partner'

    document_type_sunat_id = fields.Many2one(
        comodel_name='l10n_latam.identification.type',
        string='Tipo de documento en SUNAT'
    )
    number_document_sunat = fields.Char(
        string='N° de Documento en SUNAT'
    )
    type_contributor_sunat = fields.Char(
        string='Tipo de Contribuyente'
    )
    type_document_sunat = fields.Char(
        string='Tipo de Documento'
    )
    date_inscription_sunat = fields.Date(
        string='Fecha de Inscripción',
        help='Aquí se consigna la fecha de acuerdo con SUNAT, '
             'pero en caso la fecha sea anterior al año "1900", se consignará "01/01/1900"'
    )
    date_start_activity_sunat = fields.Date(
        string='Fecha de inicio de Actividades',
        help='Aquí se consigna la fecha de acuerdo con SUNAT, '
             'pero en caso la fecha sea anterior al año "1900", se consignará "01/01/1900"'
    )
    ple_date_sunat = fields.Date(
        string='Afiliado al PLE desde'
    )
    emissor_date_sunat = fields.Date(
        string='Emisor electrónico desde'
    )
    document_electronic_sunat = fields.Char(
        string='Comprobantes electrónico'
    )
    state_contributor_sunat = fields.Char(
        string='Estado del contribuyente'
    )
    condition_contributor_sunat = fields.Char(
        string='Condición del Contribuyente'
    )
    office_sunat = fields.Char(
        string='Profesión u Oficio'
    )
    system_emission_sunat = fields.Char(
        string='Sistema de emisión del comprobante'
    )
    system_account_sunat = fields.Char(
        string='Sistema de contabilidad'
    )
    foreign_activity_commerce_sunat = fields.Char(
        string='Actividad de comercio exterior'
    )
    activity_economic_ids = fields.One2many(
        comodel_name='activity.economic.sunat',
        inverse_name='partner_id',
        string='Actividad(es) Económica(s)'
    )
    document_pay_ids = fields.One2many(
        comodel_name='document.pay.sunat',
        inverse_name='partner_id',
        string='Comprobantes de Pago c/aut. de impresión (F. 806 u 816)'
    )
    system_electronic_ids = fields.One2many(
        comodel_name='system.electronic.sunat',
        inverse_name='partner_id',
        string='Sistema de Emision Electronica'
    )
    pattern_sunat_ids = fields.One2many(
        comodel_name='pattern.sunat',
        inverse_name='partner_id',
        string='Padrones'
    )

    @api.model
    def action_validate_sunat(self, partner):
        partner_id = partner.get('id')
        vat = partner.get('vat')
        document_type = int(partner.get('l10n_latam_identification_type_id'))
        token_api = self.env.company.token_api_ruc
        if document_type and vat and token_api:
            document_type_code = self.env['l10n_latam.identification.type'].browse(document_type).l10n_pe_vat_code
            obj_sunat_conflux = SunatPartnerConflux(vat, document_type_code, token_api)
            values = obj_sunat_conflux.action_validate_api()
            if values and values.get('document_type_sunat_id'):
                obj_document_type_origin = self.env['l10n_latam.identification.type'].search([('l10n_pe_vat_code', '=', values['document_type_sunat_id'])], limit=1)
                values.update({'document_type_sunat_id': obj_document_type_origin.id})
                values.update({'l10n_latam_identification_type_id': obj_document_type_origin.id})
                if document_type_code == '6':
                    if values['state_id']:
                        state_id = self.env['res.country.state'].search([
                            ('code', '=', values['state_id']),
                            ('country_id', '=', self.env.ref('base.pe').id)], limit=1)
                        values['state_id'] = state_id.id if state_id else False
                    if values['city_id']:
                        city_id = self.env['res.city'].search([
                            ('l10n_pe_code', '=', values['city_id']),
                            ('country_id', '=', self.env.ref('base.pe').id)], limit=1)
                        values['city_id'] = city_id.id if city_id else False
                    if values['l10n_pe_district']:
                        l10n_pe_district = self.env['l10n_pe.res.city.district'].search([('code', '=', values['l10n_pe_district'])], limit=1)
                        values['l10n_pe_district'] = l10n_pe_district.id if l10n_pe_district else False
                if partner_id:
                    obj_partner = self.browse(partner_id)
                    obj_partner.activity_economic_ids.unlink()
                    obj_partner.document_pay_ids.unlink()
                    obj_partner.system_electronic_ids.unlink()
                    obj_partner.pattern_sunat_ids.unlink()
                    obj_partner.write(values)
                else:
                    partner_id = self.create(values).id
            else:
                partner_id = False
        return partner_id

    def action_ruc_validation_sunat(self):
        self.ensure_one()
        values = {
            'vat': self.vat,
            'l10n_latam_identification_type_id': self.l10n_latam_identification_type_id.id,
            'id': self.id
        }
        if not self.action_validate_sunat(values):
            raise Warning(
                'No se puede realizar la consulta, porque el servicio de SUNAT está demorando en Responder, o su conexión a Internet es demasiado lenta. '
                'Pruebe haciendo la consulta manual directo en la página de consulta RUC de SUNAT, porque si el servicio de SUNAT presenta problemas de '
                'lentitud, Odoo no se conectará para evitar afectar el rendimiento del sistema.')
        return True

    '''@api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(ResPartner, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            peruvian_company = self.env.company.get_fiscal_country() == self.env.ref('base.pe')
            if peruvian_company:
                return res
            doc = etree.XML(res['arch'])
            tags = [('button', 'action_ruc_validation_sunat'), ('page', 'ruc_sunat')]
            for tag in tags:
                for node in doc.xpath("//{}[@name='{}']".format(tag[0], tag[1])):
                    modifiers = json.loads(node.get("modifiers") or '{}')
                    modifiers['invisible'] = 1
                    node.set("modifiers", json.dumps(modifiers))
            res['arch'] = etree.tostring(doc, encoding='unicode')
        return res'''


class ResCompany(models.Model):
    _inherit = 'res.company'

    token_api_ruc = fields.Char(string='Token consulta RUC')
