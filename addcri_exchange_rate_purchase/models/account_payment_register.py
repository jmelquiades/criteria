
from odoo import models, fields, api, _


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'
    _description = 'Register Payment'

    exchange_currency_manual = fields.Float('Tipo de cambio',  digits=(12, 3))
    onchange_exchange_currency = fields.Boolean('Onchange Exchange Currency', default=False)

    def _create_payment_vals_from_wizard(self):
        payment_vals = super(AccountPaymentRegister, self)._create_payment_vals_from_wizard()
        payment_vals.update({
                'exchange_currency_manual': self.exchange_currency_manual,
                'onchange_exchange_currency': self.onchange_exchange_currency,
                })
        return payment_vals
    
    @api.onchange('payment_date', 'payment_type', 'currency_id')
    def _onchange_date_payment(self):
        if self.payment_type == 'inbound':
            self.exchange_currency_manual = self.currency_id._get_conversion_purchase_rate(self.currency_id, self.company_id.currency_id, self.company_id, self.payment_date)
        elif self.payment_type == 'outbound':
            self.exchange_currency_manual = self.currency_id._get_conversion_sale_rate(self.currency_id, self.company_id.currency_id, self.company_id, self.payment_date)
        else:
            self.exchange_currency_manual = self.currency_id._get_conversion_rate(self.currency_id, self.company_id.currency_id, self.company_id, self.payment_date)


    @api.onchange('exchange_currency_manual')
    def _onchange_exchange_currency_manual(self):
        if self.payment_type == 'inbound' and self.exchange_currency_manual != self.currency_id._get_conversion_purchase_rate(self.currency_id, self.company_id.currency_id, self.company_id, self.payment_date):
            self.onchange_exchange_currency = True
        elif self.payment_type == 'outbound' and self.exchange_currency_manual != self.currency_id._get_conversion_sale_rate(self.currency_id, self.company_id.currency_id, self.company_id, self.payment_date):
            self.onchange_exchange_currency = True
        elif self.payment_type not in ('inbound', 'outbound') and self.exchange_currency_manual != self.currency_id._get_conversion_rate(self.currency_id, self.company_id.currency_id, self.company_id, self.payment_date):
            self.onchange_exchange_currency = True
        else:
            self.onchange_exchange_currency = False

