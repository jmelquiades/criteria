from odoo import _, api, fields, models
from odoo.exceptions import UserError

class AccountPayment(models.Model):
    _inherit = 'account.payment'
    _description = 'Account Payment'

    exchange_currency_manual = fields.Float('Tipo de cambio')
    onchange_exchange_currency = fields.Boolean('Onchange Exchange Currency', default=False)

    @api.onchange('date', 'payment_type', 'currency_id')
    def _onchange_date_payment(self):
        if self.payment_type == 'inbound':
            self.exchange_currency_manual = self.currency_id._get_conversion_purchase_rate(self.currency_id, self.company_id.currency_id, self.company_id, self.date)
        elif self.payment_type == 'outbound':
            self.exchange_currency_manual = self.currency_id._get_conversion_sale_rate(self.currency_id, self.company_id.currency_id, self.company_id, self.date)
        else:
            self.exchange_currency_manual = self.currency_id._get_conversion_rate(self.currency_id, self.company_id.currency_id, self.company_id, self.date)


    @api.onchange('exchange_currency_manual')
    def _onchange_exchange_currency_manual(self):
        if self.payment_type == 'inbound' and self.exchange_currency_manual != self.currency_id._get_conversion_purchase_rate(self.currency_id, self.company_id.currency_id, self.company_id, self.date):
            self.onchange_exchange_currency = True
        elif self.payment_type == 'outbound' and self.exchange_currency_manual != self.currency_id._get_conversion_sale_rate(self.currency_id, self.company_id.currency_id, self.company_id, self.date):
            self.onchange_exchange_currency = True
        elif self.payment_type not in ('inbound', 'outbound') and self.exchange_currency_manual != self.currency_id._get_conversion_rate(self.currency_id, self.company_id.currency_id, self.company_id, self.date):
            self.onchange_exchange_currency = True
        else:
            self.onchange_exchange_currency = False
        
    
    def _prepare_move_line_default_vals(self, write_off_line_vals=None):
        ''' Prepare the dictionary to create the default account.move.lines for the current payment.
        :param write_off_line_vals: Optional dictionary to create a write-off account.move.line easily containing:
            * amount:       The amount to be added to the counterpart amount.
            * name:         The label to set on the line.
            * account_id:   The account on which create the write-off.
        :return: A list of python dictionary to be passed to the account.move.line's 'create' method.
        '''
        self.ensure_one()
        write_off_line_vals = write_off_line_vals or {}

        if not self.outstanding_account_id:
            raise UserError(_(
                "You can't create a new payment without an outstanding payments/receipts account set either on the company or the %s payment method in the %s journal.",
                self.payment_method_line_id.name, self.journal_id.display_name))

        # Compute amounts.
        write_off_amount_currency = write_off_line_vals.get('amount', 0.0)

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
                self.date,
            )
            liquidity_balance = convert(
                liquidity_amount_currency,
                self.company_id.currency_id,
                self.company_id,
                self.date,
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

        if self.is_internal_transfer:
            if self.payment_type == 'inbound':
                liquidity_line_name = _('Transfer to %s', self.journal_id.name)
            else: # payment.payment_type == 'outbound':
                liquidity_line_name = _('Transfer from %s', self.journal_id.name)
        else:
            liquidity_line_name = self.payment_reference

        # Compute a default label to set on the journal items.

        payment_display_name = self._prepare_payment_display_name()

        default_line_name = self.env['account.move.line']._get_default_line_name(
            _("Internal Transfer") if self.is_internal_transfer else payment_display_name['%s-%s' % (self.payment_type, self.partner_type)],
            self.amount,
            self.currency_id,
            self.date,
            partner=self.partner_id,
        )

        line_vals_list = [
            # Liquidity line.
            {
                'name': liquidity_line_name or default_line_name,
                'date_maturity': self.date,
                'amount_currency': liquidity_amount_currency,
                'currency_id': currency_id,
                'debit': liquidity_balance if liquidity_balance > 0.0 else 0.0,
                'credit': -liquidity_balance if liquidity_balance < 0.0 else 0.0,
                'partner_id': self.partner_id.id,
                'account_id': self.outstanding_account_id.id,
            },
            # Receivable / Payable.
            {
                'name': self.payment_reference or default_line_name,
                'date_maturity': self.date,
                'amount_currency': counterpart_amount_currency,
                'currency_id': currency_id,
                'debit': counterpart_balance if counterpart_balance > 0.0 else 0.0,
                'credit': -counterpart_balance if counterpart_balance < 0.0 else 0.0,
                'partner_id': self.partner_id.id,
                'account_id': self.destination_account_id.id,
            },
        ]
        if not self.currency_id.is_zero(write_off_amount_currency):
            # Write-off line.
            line_vals_list.append({
                'name': write_off_line_vals.get('name') or default_line_name,
                'amount_currency': write_off_amount_currency,
                'currency_id': currency_id,
                'debit': write_off_balance if write_off_balance > 0.0 else 0.0,
                'credit': -write_off_balance if write_off_balance < 0.0 else 0.0,
                'partner_id': self.partner_id.id,
                'account_id': write_off_line_vals.get('account_id'),
            })
        return line_vals_list