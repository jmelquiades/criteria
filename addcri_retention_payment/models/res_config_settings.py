from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    retention_journal_id = fields.Many2one('account.journal', related='company_id.retention_journal_id', string="Retention Journal", readonly=False)
