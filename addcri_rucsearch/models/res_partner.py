from odoo import _, api, fields, models
import requests
import json
from odoo.exceptions import Warning, UserError

import logging
_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    def _default_country(self):
        return self.env.company.country_id.id
    
    country_id = fields.Many2one(default=_default_country)
    commercial_name = fields.Char(string="Nombre Comercial")
    state = fields.Selection([('habido','Habido'), ('nhabido','No Habido')], string="Estado")
    alert_warning_vat = fields.Boolean(string="Alerta de Peligro RUC", default = False)
    
    @api.onchange('vat','l10n_latam_identification_type_id')
    def onchange_vat(self):
        res = {}
        self.name = False
        self.commercial_name = False
        self.street = False
        if self.vat:
            if self.l10n_latam_identification_type_id.l10n_pe_vat_code == '6':
                if len(self.vat) != 11 :
                    res['warning'] = {'title': _('Peligro'), 'message': _('El RUC debe tener 11 caracteres')}
                else:
                    company = self.env['res.company'].browse(self.env.company.id)
                    if company.l10n_pe_rucsearch == True:
                        self.get_data_ruc()
        if res:
            return res
    
    @api.model
    def l10n_pe_ruc_connection(self, ruc):
        data = {}
        if self.env.user.company_id.l10n_pe_api_ruc_connection == 'sunat':
            data = self.sunat_connection(ruc)
        return data            
        
    @api.model    
    def sunat_connection(self, ruc):
        url = 'https://mobsu.codigo91.com/api/search/index.php?nruc={ruc}&nlic=5b9ffcdd81c21'
        data = {}
        try:
            i = 0;
            while i <= 1:
                r = requests.get(url.format(ruc=ruc),headers={"User-Agent": "XY"})
                result = r.json()
                api_success = result.get('success')
                if api_success == True:
                    data['api_success'] = api_success
                    data['ruc'] = result.get('result').get('ruc')
                    data['business_name'] = result.get('result').get('razon_social')
                    data['type_of_taxpayer'] = result.get('result').get('tipo')
                    data['estado'] = result.get('result').get('estado')
                    data['contributing_condition'] = result.get('result').get('condicion')
                    data['commercial_name'] = result.get('result').get('nombre_comercial')
                    address = result.get('result').get('direccion')
                    district = result.get('result').get('distrito').title()
                    province = result.get('result').get('provincia').title()
                    prov_ids = self.env['res.city'].search([('name', '=', province),('state_id','!=',False)])
                    dist_id = self.env['l10n_pe.res.city.district'].search([('name', '=', district),('city_id', 'in', [x.id for x in prov_ids])], limit=1)
                    dist_short_id = self.env['l10n_pe.res.city.district'].search([('name', '=', district)], limit=1)
                    if dist_id:
                        l10n_pe_district = dist_id
                    else:
                        l10n_pe_district = dist_short_id

                    vals = {}
                    if l10n_pe_district:
                        vals['district_id'] = l10n_pe_district.id
                        vals['city_id'] = l10n_pe_district.city_id.id
                        vals['state_id'] = l10n_pe_district.city_id.state_id.id
                        vals['country_id'] = l10n_pe_district.city_id.state_id.country_id.id
                    data['value'] = vals
                    data['residence'] = str(address).strip()
                    break
                else:
                    data['api_success'] = api_success
                    i += 1

        except Exception:
            self.alert_warning_vat = True
            data = False
        return data
    
    def get_data_ruc(self):
        result = self.l10n_pe_ruc_connection(self.vat)
        if result:
            if result['api_success'] == True:
                self.alert_warning_vat = False
                self.company_type = 'company'
                self.name = str(result['business_name']).strip()
                self.commercial_name = str(result['commercial_name'] or result['business_name']).strip()
                self.street = str(result['residence']).strip()
                self.street_name = "PRUEBA"
                if result['contributing_condition'] == 'HABIDO':
                    self.state = 'habido'
                else:
                    self.state = 'nhabido'
                if result['value']:
                    print(result['value'])
                    self.l10n_pe_district = result['value']['district_id']
                    self.city_id = result['value']['city_id']
                    self.state_id = result['value']['state_id']
                    self.country_id = result['value']['country_id']
            else:
                self.alert_warning_vat = True
        
    @api.onchange('l10n_pe_district')
    def _onchange_l10n_pe_district(self):
        if self.l10n_pe_district and self.l10n_pe_district.city_id:
            self.city_id = self.l10n_pe_district.city_id
        
    @api.onchange('city_id')
    def _onchange_city_id(self):
        if self.city_id and self.city_id.state_id:
            self.state_id = self.city_id.state_id
        res = {}
        res['domain'] = {}
        res['domain']['l10n_pe_district'] = []
        if self.city_id:
            res['domain']['l10n_pe_district'] += [('city_id','=',self.city_id.id)]
        return res

    @api.onchange('state_id')
    def _onchange_state_id(self):
        if self.state_id and self.state_id.country_id:
            self.country_id = self.state_id.country_id
        res = {}
        res['domain'] = {}
        res['domain']['city_id'] = []
        if self.state_id:
            res['domain']['city_id'] += [('state_id','=',self.state_id.id)]
        return res