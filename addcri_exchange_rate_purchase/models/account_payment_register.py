
from odoo import models, fields, api, _


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'
    _description = 'Register Payment'

    exchange_currency_manual = fields.Float('Tipo de cambio manual')

    def _create_payment_vals_from_wizard(self):
        payment_vals = super(AccountPaymentRegister, self)._create_payment_vals_from_wizard()
        payment_vals.update({
                'exchange_currency_manual': self.exchange_currency_manual
                })
        return payment_vals

