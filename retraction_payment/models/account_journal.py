from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountJournal(models.Model):
    _inherit = 'account.journal'
    _description = 'Account Journal'

    detraction_journal = fields.Boolean('Detraction Journal', default=False)

    @api.constrains('detraction_journal')
    def _constrains_detraction_journal(self):
        detraction_journals = self.env['account.journal'].search_count([('detraction_journal', '=', True)])
        if detraction_journals >= 1:
            raise UserError('No puede existir más de un diario de detracción.')
