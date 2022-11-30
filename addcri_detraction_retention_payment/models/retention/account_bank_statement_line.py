from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'
    _description = 'Account Bank Statement Line'

    l10n_latam_document_type_id = fields.Many2one('l10n_latam.document.type', string='Tipo de documento')
    l10n_latam_table_10_id = fields.Many2one('sunat.table.10', string='Tabla 10')
