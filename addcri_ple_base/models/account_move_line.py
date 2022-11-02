from odoo import _, api, fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    correlative = fields.Char(
        string='Correlativo'
    )
