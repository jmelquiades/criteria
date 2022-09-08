from datetime import date, datetime, timedelta

from odoo import models, fields, api, _
from odoo.fields import Date, Datetime
from odoo.exceptions import ValidationError, UserError, AccessError

class ResCompany(models.Model):
    _inherit = 'res.company'
    
    l10n_pe_rucsearch = fields.Boolean(string="ADDCRI - RUC SEARCH")
    l10n_pe_api_ruc_connection = fields.Selection([
        ('sunat', 'Sunat')
    ], string='Api RUC Connection', default='sunat')
    
    @api.onchange('country_id')
    def _onchange_country_id(self):
        super(ResCompany, self)._onchange_country_id()
        if self.country_id and self.country_id.code == 'PE':
            self.l10n_pe_rucsearch = True
        else:
            self.l10n_pe_rucsearch = False
