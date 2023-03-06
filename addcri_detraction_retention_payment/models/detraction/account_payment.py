from odoo import _, api, fields, models

class AccountPayment(models.Model):
    _inherit = 'account.payment'
    _description = 'Account Payment'
    
    detraction = fields.Boolean('Pago de detracción')