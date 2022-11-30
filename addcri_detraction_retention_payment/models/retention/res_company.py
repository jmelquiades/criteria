from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    retention_journal_id = fields.Many2one('account.journal', string='Retention Journal', copy=True, groups="account.group_account_manager")
