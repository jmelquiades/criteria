from odoo import api, fields, models
class IrConfigParameter(models.Model):
    """Per-database storage of configuration key-value pairs."""
    _inherit = 'ir.config_parameter'
    _description = 'System Parameter'

    def init(self, force=False):
        super(IrConfigParameter, self).init(force=force)
        if force:
            companies = self.env['res.company'].search([])
            if companies:
                companies.write({'l10n_pe_dte_service_provider': 'SUNATTEST'})