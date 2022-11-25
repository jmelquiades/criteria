from odoo import _, api, fields, models


class AccountJournal(models.Model):
    _inherit = 'account.journal'
    _description = 'Account Journal'

    sequence_id = fields.Many2one('ir.sequence', string='Secuencia')
