from odoo import _, api, fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    _description = 'Account Move Line'

    # @api.model
    # def _get_fields_onchange_subtotal_model(self, price_subtotal, move_type, currency, company, date):
    #     ''' This method is used to recompute the values of 'amount_currency', 'debit', 'credit' due to a change made
    #     in some business fields (affecting the 'price_subtotal' field).

    #     :param price_subtotal:  The untaxed amount.
    #     :param move_type:       The type of the move.
    #     :param currency:        The line's currency.
    #     :param company:         The move's company.
    #     :param date:            The move's date.
    #     :return:                A dictionary containing 'debit', 'credit', 'amount_currency'.
    #     '''
    #     if move_type in self.move_id.get_outbound_types():
    #         sign = 1
    #     elif move_type in self.move_id.get_inbound_types():
    #         sign = -1
    #     else:
    #         sign = 1

    #     amount_currency = price_subtotal * sign
    #     balance = currency._convert(amount_currency, company.currency_id, company, date or fields.Date.context_today(self))
    #     return {
    #         'amount_currency': amount_currency,
    #         'currency_id': currency.id,
    #         'debit': balance > 0.0 and balance or 0.0,
    #         'credit': balance < 0.0 and -balance or 0.0,
    #     }

    # @api.onchange('amount_currency')
    # def _onchange_amount_currency(self):
    #     for line in self:
    #         company = line.move_id.company_id
    #         balance = line.currency_id._convert(line.amount_currency, company.currency_id, company, line.move_id.date or fields.Date.context_today(line))
    #         line.debit = balance if balance > 0.0 else 0.0
    #         line.credit = -balance if balance < 0.0 else 0.0

    #         if not line.move_id.is_invoice(include_receipts=True):
    #             continue

    #         line.update(line._get_fields_onchange_balance())
    #         line.update(line._get_price_total_and_subtotal())

    # @api.onchange('currency_id')
    # def _onchange_currency(self):
    #     for line in self:
    #         company = line.move_id.company_id

    #         if line.move_id.is_invoice(include_receipts=True):
    #             line._onchange_price_subtotal()
    #         elif not line.move_id.reversed_entry_id:
    #             balance = line.currency_id._convert(line.amount_currency, company.currency_id, company, line.move_id.date or fields.Date.context_today(line))
    #             line.debit = balance if balance > 0.0 else 0.0
    #             line.credit = -balance if balance < 0.0 else 0.0

    # def _prepare_reconciliation_partials(self):
    #     ''' Prepare the partials on the current journal items to perform the reconciliation.
    #     /!\ The order of records in self is important because the journal items will be reconciled using this order.

    #     :return: A recordset of account.partial.reconcile.
    #     '''
    #     def fix_remaining_cent(currency, abs_residual, partial_amount):
    #         if abs_residual - currency.rounding <= partial_amount <= abs_residual + currency.rounding:
    #             return abs_residual
    #         else:
    #             return partial_amount

    #     debit_lines = iter(self.filtered(lambda line: line.balance > 0.0 or line.amount_currency > 0.0 and not line.reconciled))
    #     credit_lines = iter(self.filtered(lambda line: line.balance < 0.0 or line.amount_currency < 0.0 and not line.reconciled))
    #     void_lines = iter(self.filtered(lambda line: not line.balance and not line.amount_currency and not line.reconciled))
    #     debit_line = None
    #     credit_line = None

    #     debit_amount_residual = 0.0
    #     debit_amount_residual_currency = 0.0
    #     credit_amount_residual = 0.0
    #     credit_amount_residual_currency = 0.0
    #     debit_line_currency = None
    #     credit_line_currency = None

    #     partials_vals_list = []

    #     while True:

    #         # Move to the next available debit line.
    #         if not debit_line:
    #             debit_line = next(debit_lines, None) or next(void_lines, None)
    #             if not debit_line:
    #                 break
    #             debit_amount_residual = debit_line.amount_residual

    #             if debit_line.currency_id:
    #                 debit_amount_residual_currency = debit_line.amount_residual_currency
    #                 debit_line_currency = debit_line.currency_id
    #             else:
    #                 debit_amount_residual_currency = debit_amount_residual
    #                 debit_line_currency = debit_line.company_currency_id

    #         # Move to the next available credit line.
    #         if not credit_line:
    #             credit_line = next(void_lines, None) or next(credit_lines, None)
    #             if not credit_line:
    #                 break
    #             credit_amount_residual = credit_line.amount_residual

    #             if credit_line.currency_id:
    #                 credit_amount_residual_currency = credit_line.amount_residual_currency
    #                 credit_line_currency = credit_line.currency_id
    #             else:
    #                 credit_amount_residual_currency = credit_amount_residual
    #                 credit_line_currency = credit_line.company_currency_id

    #         min_amount_residual = min(debit_amount_residual, -credit_amount_residual)

    #         if debit_line_currency == credit_line_currency:
    #             # Reconcile on the same currency.

    #             min_amount_residual_currency = min(debit_amount_residual_currency, -credit_amount_residual_currency)
    #             min_debit_amount_residual_currency = min_amount_residual_currency
    #             min_credit_amount_residual_currency = min_amount_residual_currency

    #         else:
    #             # Reconcile on the company's currency.

    #             min_debit_amount_residual_currency = credit_line.company_currency_id._convert(
    #                 min_amount_residual,
    #                 debit_line.currency_id,
    #                 credit_line.company_id,
    #                 credit_line.date,
    #             )
    #             min_debit_amount_residual_currency = fix_remaining_cent(
    #                 debit_line.currency_id,
    #                 debit_amount_residual_currency,
    #                 min_debit_amount_residual_currency,
    #             )
    #             min_credit_amount_residual_currency = debit_line.company_currency_id._convert(
    #                 min_amount_residual,
    #                 credit_line.currency_id,
    #                 debit_line.company_id,
    #                 debit_line.date,
    #             )
    #             min_credit_amount_residual_currency = fix_remaining_cent(
    #                 credit_line.currency_id,
    #                 -credit_amount_residual_currency,
    #                 min_credit_amount_residual_currency,
    #             )

    #         debit_amount_residual -= min_amount_residual
    #         debit_amount_residual_currency -= min_debit_amount_residual_currency
    #         credit_amount_residual += min_amount_residual
    #         credit_amount_residual_currency += min_credit_amount_residual_currency

    #         partials_vals_list.append({
    #             'amount': min_amount_residual,
    #             'debit_amount_currency': min_debit_amount_residual_currency,
    #             'credit_amount_currency': min_credit_amount_residual_currency,
    #             'debit_move_id': debit_line.id,
    #             'credit_move_id': credit_line.id,
    #         })

    #         has_debit_residual_left = not debit_line.company_currency_id.is_zero(debit_amount_residual) and debit_amount_residual > 0.0
    #         has_credit_residual_left = not credit_line.company_currency_id.is_zero(credit_amount_residual) and credit_amount_residual < 0.0
    #         has_debit_residual_curr_left = not debit_line_currency.is_zero(debit_amount_residual_currency) and debit_amount_residual_currency > 0.0
    #         has_credit_residual_curr_left = not credit_line_currency.is_zero(credit_amount_residual_currency) and credit_amount_residual_currency < 0.0

    #         if debit_line_currency == credit_line_currency:
    #             # The debit line is now fully reconciled because:
    #             # - either amount_residual & amount_residual_currency are at 0.
    #             # - either the credit_line is not an exchange difference one.
    #             if not has_debit_residual_curr_left and (has_credit_residual_curr_left or not has_debit_residual_left):
    #                 debit_line = None

    #             # The credit line is now fully reconciled because:
    #             # - either amount_residual & amount_residual_currency are at 0.
    #             # - either the debit is not an exchange difference one.
    #             if not has_credit_residual_curr_left and (has_debit_residual_curr_left or not has_credit_residual_left):
    #                 credit_line = None

    #         else:
    #             # The debit line is now fully reconciled since amount_residual is 0.
    #             if not has_debit_residual_left:
    #                 debit_line = None

    #             # The credit line is now fully reconciled since amount_residual is 0.
    #             if not has_credit_residual_left:
    #                 credit_line = None

    #     return partials_vals_list
