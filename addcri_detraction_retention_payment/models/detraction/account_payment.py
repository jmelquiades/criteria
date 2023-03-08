from odoo import _, api, fields, models

class AccountPayment(models.Model):
    _inherit = 'account.payment'
    _description = 'Account Payment'
    
    detraction = fields.Boolean('Pago de detracción')
    invoice_date = fields.Date('Invoice Date')

    def _prepare_vals_debit_credit_amount_currency(self, write_off_amount_currency):
        if self.payment_type == 'inbound':
            # Receive money.
            liquidity_amount_currency = self.amount
        elif self.payment_type == 'outbound':
            # Send money.
            liquidity_amount_currency = -self.amount
            write_off_amount_currency *= -1
        else:
            liquidity_amount_currency = write_off_amount_currency = 0.0

        if not self.is_internal_transfer and not self.onchange_exchange_currency:
            if self.payment_type == 'inbound':
                convert = getattr(self.currency_id, '_convert_purchase')
            elif self.payment_type == 'outbound':
                convert = getattr(self.currency_id, '_convert_sale')
            else:
                convert = getattr(self.currency_id, '_convert')

            write_off_balance = convert(
                write_off_amount_currency,
                self.company_id.currency_id,
                self.company_id,
                self.date if not self.detraction else self.invoice_date,
            )
            liquidity_balance = convert(
                liquidity_amount_currency,
                self.company_id.currency_id,
                self.company_id,
                self.date if not self.detraction else self.invoice_date,
            )
        else:
            if self.currency_id != self.company_id.currency_id:
                write_off_balance = write_off_amount_currency * self.exchange_currency_manual
                liquidity_balance = liquidity_amount_currency * self.exchange_currency_manual
            else:
                write_off_balance = write_off_amount_currency
                liquidity_balance = liquidity_amount_currency

        counterpart_amount_currency = -liquidity_amount_currency - write_off_amount_currency
        counterpart_balance = -liquidity_balance - write_off_balance
        currency_id = self.currency_id.id

        return liquidity_amount_currency, liquidity_balance, write_off_balance, counterpart_amount_currency, counterpart_balance, currency_id