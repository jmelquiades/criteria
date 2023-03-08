from odoo import _, api, fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    _description = 'Account Move Line'

    exchange_rate = fields.Float('Tipo de cambio',  digits=(12, 3))

    @api.model
    def _get_fields_onchange_subtotal_model(self, price_subtotal, move_type, currency, company, date):
        res = super(AccountMoveLine, self)._get_fields_onchange_subtotal_model(price_subtotal, move_type, currency, company, date)
        if move_type in self.move_id.get_outbound_types():
            sign = 1
        elif move_type in self.move_id.get_inbound_types():
            sign = -1
        else:
            sign = 1

        amount_currency = price_subtotal * sign
        if move_type in self.move_id.get_inbound_types():
            balance = currency._convert_purchase(amount_currency, company.currency_id, company, date or fields.Date.context_today(self), exchange_rate=self.move_id.exchange_rate)
        elif move_type in self.move_id.get_outbound_types():
            balance = currency._convert_sale(amount_currency, company.currency_id, company, date or fields.Date.context_today(self), exchange_rate=self.move_id.exchange_rate)
        else:
            balance = currency._convert_purchase(amount_currency, company.currency_id, company, date or fields.Date.context_today(self))
        res['balance'] = balance
        res['debit'] = balance > 0.0 and balance or 0.0
        res['credit'] = balance < 0.0 and -balance or 0.0

        return res

    @api.onchange('quantity', 'discount', 'price_unit', 'tax_ids')
    def _onchange_price_subtotal(self):
        for line in self:
            line.exchange_rate = line.move_id.exchange_rate
        super(AccountMoveLine, self)._onchange_price_subtotal()
        