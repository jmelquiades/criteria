from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'
    _description = 'Account Bank Statement'

    retention = fields.Boolean('retention', compute='_get_retention')

    @api.depends('journal_id', 'company_id')
    def _get_retention(self):
        for record in self:
            if record._get_retention_journal() == record.journal_id:
                record.retention = True
            else:
                record.retention = False

    def _get_retention_journal(self):
        retention = self.env.user.company_id.retention_journal_id
        if not retention:
            raise UserError('Configurar el diario de retenciones.')
        else:
            return retention
