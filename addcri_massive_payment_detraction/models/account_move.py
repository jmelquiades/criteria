from odoo import _, api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'
    _description = 'Account Move'

    massive_payment_detraction_id = fields.Many2one('massive.payment.detraction', string='Pagos masivos')
