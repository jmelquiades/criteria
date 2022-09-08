from odoo import api, fields, models, _

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    l10n_pe_rucsearch = fields.Boolean(string="ADDCRI - RUC SEARCH", related='company_id.l10n_pe_rucsearch', readonly=False)
