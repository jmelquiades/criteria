from odoo import _, api, fields, models
import logging


_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'
    _description = 'Account Move'

    exchange_rate = fields.Float('Tipo de cambio',  digits=(12, 3), store=True, compute='_get_exchange_rate', readonly=False)
    if_foreign_currency = fields.Boolean('Is foreign currency?', compute='_get_if_foreign_currency')

    @api.depends('currency_id', 'company_id.currency_id')
    def _get_if_foreign_currency(self):
        for record in self:
            record.if_foreign_currency = record.currency_id != record.company_id.currency_id

    @api.depends('date', 'currency_id', 'company_id', 'company_id.currency_id')
    def _get_exchange_rate(self):
        for record in self:
            record.exchange_rate = 1
            if record.move_type in record.get_inbound_types():
                record.exchange_rate = record.company_id.currency_id._get_conversion_purchase_rate(record.currency_id, record.company_id.currency_id, record.company_id, record.date)
            elif record.move_type in record.get_outbound_types():
                record.exchange_rate = record.company_id.currency_id._get_conversion_sale_rate(record.currency_id, record.company_id.currency_id, record.company_id, record.date)

    @api.onchange('exchange_rate')
    def _onchange_price_subtotal_from_exchange_rate(self):
        lines = (self.line_ids | self.invoice_line_ids).with_context(manual_rate=True)
        lines._onchange_price_subtotal()

    # def _recompute_tax_lines(self, recompute_tax_base_amount=False, tax_rep_lines_to_recompute=None):
    #     """ Compute the dynamic tax lines of the journal entry.

    #     :param recompute_tax_base_amount: Flag forcing only the recomputation of the `tax_base_amount` field.
    #     """
    #     self.ensure_one()
    #     in_draft_mode = self != self._origin

    #     def _serialize_tax_grouping_key(grouping_dict):
    #         ''' Serialize the dictionary values to be used in the taxes_map.
    #         :param grouping_dict: The values returned by '_get_tax_grouping_key_from_tax_line' or '_get_tax_grouping_key_from_base_line'.
    #         :return: A string representing the values.
    #         '''
    #         return '-'.join(str(v) for v in grouping_dict.values())

    #     def _compute_base_line_taxes(base_line):
    #         ''' Compute taxes amounts both in company currency / foreign currency as the ratio between
    #         amount_currency & balance could not be the same as the expected currency rate.
    #         The 'amount_currency' value will be set on compute_all(...)['taxes'] in multi-currency.
    #         :param base_line:   The account.move.line owning the taxes.
    #         :return:            The result of the compute_all method.
    #         '''
    #         move = base_line.move_id

    #         if move.is_invoice(include_receipts=True):
    #             handle_price_include = True
    #             sign = -1 if move.is_inbound() else 1
    #             quantity = base_line.quantity
    #             is_refund = move.move_type in ('out_refund', 'in_refund')
    #             price_unit_wo_discount = sign * base_line.price_unit * (1 - (base_line.discount / 100.0))
    #         else:
    #             handle_price_include = False
    #             quantity = 1.0
    #             tax_type = base_line.tax_ids[0].type_tax_use if base_line.tax_ids else None
    #             is_refund = (tax_type == 'sale' and base_line.debit) or (tax_type == 'purchase' and base_line.credit)
    #             price_unit_wo_discount = base_line.amount_currency

    #         return base_line.tax_ids._origin.with_context(force_sign=move._get_tax_force_sign()).compute_all(
    #             price_unit_wo_discount,
    #             currency=base_line.currency_id,
    #             quantity=quantity,
    #             product=base_line.product_id,
    #             partner=base_line.partner_id,
    #             is_refund=is_refund,
    #             handle_price_include=handle_price_include,
    #             include_caba_tags=move.always_tax_exigible,
    #         )

    #     taxes_map = {}

    #     # ==== Add tax lines ====
    #     to_remove = self.env['account.move.line']
    #     for line in self.line_ids.filtered('tax_repartition_line_id'):
    #         grouping_dict = self._get_tax_grouping_key_from_tax_line(line)
    #         grouping_key = _serialize_tax_grouping_key(grouping_dict)
    #         if grouping_key in taxes_map:
    #             # A line with the same key does already exist, we only need one
    #             # to modify it; we have to drop this one.
    #             to_remove += line
    #         else:
    #             taxes_map[grouping_key] = {
    #                 'tax_line': line,
    #                 'amount': 0.0,
    #                 'tax_base_amount': 0.0,
    #                 'grouping_dict': False,
    #             }
    #     if not recompute_tax_base_amount:
    #         self.line_ids -= to_remove

    #     # ==== Mount base lines ====
    #     for line in self.line_ids.filtered(lambda line: not line.tax_repartition_line_id):
    #         # Don't call compute_all if there is no tax.
    #         if not line.tax_ids:
    #             if not recompute_tax_base_amount:
    #                 line.tax_tag_ids = [(5, 0, 0)]
    #             continue

    #         compute_all_vals = _compute_base_line_taxes(line)

    #         # Assign tags on base line
    #         if not recompute_tax_base_amount:
    #             line.tax_tag_ids = compute_all_vals['base_tags'] or [(5, 0, 0)]

    #         for tax_vals in compute_all_vals['taxes']:
    #             grouping_dict = self._get_tax_grouping_key_from_base_line(line, tax_vals)
    #             grouping_key = _serialize_tax_grouping_key(grouping_dict)

    #             tax_repartition_line = self.env['account.tax.repartition.line'].browse(tax_vals['tax_repartition_line_id'])
    #             tax = tax_repartition_line.invoice_tax_id or tax_repartition_line.refund_tax_id

    #             taxes_map_entry = taxes_map.setdefault(grouping_key, {
    #                 'tax_line': None,
    #                 'amount': 0.0,
    #                 'tax_base_amount': 0.0,
    #                 'grouping_dict': False,
    #             })
    #             taxes_map_entry['amount'] += tax_vals['amount']
    #             taxes_map_entry['tax_base_amount'] += self._get_base_amount_to_display(tax_vals['base'], tax_repartition_line, tax_vals['group'])
    #             taxes_map_entry['grouping_dict'] = grouping_dict

    #     # ==== Pre-process taxes_map ====
    #     taxes_map = self._preprocess_taxes_map(taxes_map)

    #     # ==== Process taxes_map ====
    #     for taxes_map_entry in taxes_map.values():
    #         # The tax line is no longer used in any base lines, drop it.
    #         if taxes_map_entry['tax_line'] and not taxes_map_entry['grouping_dict']:
    #             if not recompute_tax_base_amount:
    #                 self.line_ids -= taxes_map_entry['tax_line']
    #             continue

    #         currency = self.env['res.currency'].browse(taxes_map_entry['grouping_dict']['currency_id'])

    #         # Don't create tax lines with zero balance.
    #         if currency.is_zero(taxes_map_entry['amount']):
    #             if taxes_map_entry['tax_line'] and not recompute_tax_base_amount:
    #                 self.line_ids -= taxes_map_entry['tax_line']
    #             continue

    #         # tax_base_amount field is expressed using the company currency.
    #         tax_base_amount = currency._convert(taxes_map_entry['tax_base_amount'], self.company_currency_id, self.company_id, self.date or fields.Date.context_today(self))

    #         # Recompute only the tax_base_amount.
    #         if recompute_tax_base_amount:
    #             if taxes_map_entry['tax_line']:
    #                 taxes_map_entry['tax_line'].tax_base_amount = tax_base_amount
    #             continue

    #         balance = currency._convert(
    #             taxes_map_entry['amount'],
    #             self.company_currency_id,
    #             self.company_id,
    #             self.date or fields.Date.context_today(self),
    #         )
    #         to_write_on_line = {
    #             'amount_currency': taxes_map_entry['amount'],
    #             'currency_id': taxes_map_entry['grouping_dict']['currency_id'],
    #             'debit': balance > 0.0 and balance or 0.0,
    #             'credit': balance < 0.0 and -balance or 0.0,
    #             'tax_base_amount': tax_base_amount,
    #         }

    #         if taxes_map_entry['tax_line']:
    #             # Update an existing tax line.
    #             if tax_rep_lines_to_recompute and taxes_map_entry['tax_line'].tax_repartition_line_id not in tax_rep_lines_to_recompute:
    #                 continue

    #             taxes_map_entry['tax_line'].update(to_write_on_line)
    #         else:
    #             # Create a new tax line.
    #             create_method = in_draft_mode and self.env['account.move.line'].new or self.env['account.move.line'].create
    #             tax_repartition_line_id = taxes_map_entry['grouping_dict']['tax_repartition_line_id']
    #             tax_repartition_line = self.env['account.tax.repartition.line'].browse(tax_repartition_line_id)

    #             if tax_rep_lines_to_recompute and tax_repartition_line not in tax_rep_lines_to_recompute:
    #                 continue

    #             tax = tax_repartition_line.invoice_tax_id or tax_repartition_line.refund_tax_id
    #             taxes_map_entry['tax_line'] = create_method({
    #                 **to_write_on_line,
    #                 'name': tax.name,
    #                 'move_id': self.id,
    #                 'company_id': self.company_id.id,
    #                 'company_currency_id': self.company_currency_id.id,
    #                 'tax_base_amount': tax_base_amount,
    #                 'exclude_from_invoice_tab': True,
    #                 **taxes_map_entry['grouping_dict'],
    #             })

    #         if in_draft_mode:
    #             taxes_map_entry['tax_line'].update(taxes_map_entry['tax_line']._get_fields_onchange_balance(force_computation=True))

    # def _recompute_cash_rounding_lines(self):
    #     ''' Handle the cash rounding feature on invoices.

    #     In some countries, the smallest coins do not exist. For example, in Switzerland, there is no coin for 0.01 CHF.
    #     For this reason, if invoices are paid in cash, you have to round their total amount to the smallest coin that
    #     exists in the currency. For the CHF, the smallest coin is 0.05 CHF.

    #     There are two strategies for the rounding:

    #     1) Add a line on the invoice for the rounding: The cash rounding line is added as a new invoice line.
    #     2) Add the rounding in the biggest tax amount: The cash rounding line is added as a new tax line on the tax
    #     having the biggest balance.
    #     '''
    #     self.ensure_one()
    #     in_draft_mode = self != self._origin

    #     def _compute_cash_rounding(self, total_amount_currency):
    #         ''' Compute the amount differences due to the cash rounding.
    #         :param self:                    The current account.move record.
    #         :param total_amount_currency:   The invoice's total in invoice's currency.
    #         :return:                        The amount differences both in company's currency & invoice's currency.
    #         '''
    #         difference = self.invoice_cash_rounding_id.compute_difference(self.currency_id, total_amount_currency)
    #         if self.currency_id == self.company_id.currency_id:
    #             diff_amount_currency = diff_balance = difference
    #         else:
    #             diff_amount_currency = difference
    #             diff_balance = self.currency_id._convert(diff_amount_currency, self.company_id.currency_id, self.company_id, self.date)
    #         return diff_balance, diff_amount_currency

    #     def _apply_cash_rounding(self, diff_balance, diff_amount_currency, cash_rounding_line):
    #         ''' Apply the cash rounding.
    #         :param self:                    The current account.move record.
    #         :param diff_balance:            The computed balance to set on the new rounding line.
    #         :param diff_amount_currency:    The computed amount in invoice's currency to set on the new rounding line.
    #         :param cash_rounding_line:      The existing cash rounding line.
    #         :return:                        The newly created rounding line.
    #         '''
    #         rounding_line_vals = {
    #             'debit': diff_balance > 0.0 and diff_balance or 0.0,
    #             'credit': diff_balance < 0.0 and -diff_balance or 0.0,
    #             'quantity': 1.0,
    #             'amount_currency': diff_amount_currency,
    #             'partner_id': self.partner_id.id,
    #             'move_id': self.id,
    #             'currency_id': self.currency_id.id,
    #             'company_id': self.company_id.id,
    #             'company_currency_id': self.company_id.currency_id.id,
    #             'is_rounding_line': True,
    #             'sequence': 9999,
    #         }

    #         if self.invoice_cash_rounding_id.strategy == 'biggest_tax':
    #             biggest_tax_line = None
    #             for tax_line in self.line_ids.filtered('tax_repartition_line_id'):
    #                 if not biggest_tax_line or tax_line.price_subtotal > biggest_tax_line.price_subtotal:
    #                     biggest_tax_line = tax_line

    #             # No tax found.
    #             if not biggest_tax_line:
    #                 return

    #             rounding_line_vals.update({
    #                 'name': _('%s (rounding)', biggest_tax_line.name),
    #                 'account_id': biggest_tax_line.account_id.id,
    #                 'tax_repartition_line_id': biggest_tax_line.tax_repartition_line_id.id,
    #                 'tax_tag_ids': [(6, 0, biggest_tax_line.tax_tag_ids.ids)],
    #                 'exclude_from_invoice_tab': True,
    #             })

    #         elif self.invoice_cash_rounding_id.strategy == 'add_invoice_line':
    #             if diff_balance > 0.0 and self.invoice_cash_rounding_id.loss_account_id:
    #                 account_id = self.invoice_cash_rounding_id.loss_account_id.id
    #             else:
    #                 account_id = self.invoice_cash_rounding_id.profit_account_id.id
    #             rounding_line_vals.update({
    #                 'name': self.invoice_cash_rounding_id.name,
    #                 'account_id': account_id,
    #             })

    #         # Create or update the cash rounding line.
    #         if cash_rounding_line:
    #             cash_rounding_line.update({
    #                 'amount_currency': rounding_line_vals['amount_currency'],
    #                 'debit': rounding_line_vals['debit'],
    #                 'credit': rounding_line_vals['credit'],
    #                 'account_id': rounding_line_vals['account_id'],
    #             })
    #         else:
    #             create_method = in_draft_mode and self.env['account.move.line'].new or self.env['account.move.line'].create
    #             cash_rounding_line = create_method(rounding_line_vals)

    #         if in_draft_mode:
    #             cash_rounding_line.update(cash_rounding_line._get_fields_onchange_balance(force_computation=True))

    #     existing_cash_rounding_line = self.line_ids.filtered(lambda line: line.is_rounding_line)

    #     # The cash rounding has been removed.
    #     if not self.invoice_cash_rounding_id:
    #         self.line_ids -= existing_cash_rounding_line
    #         return

    #     # The cash rounding strategy has changed.
    #     if self.invoice_cash_rounding_id and existing_cash_rounding_line:
    #         strategy = self.invoice_cash_rounding_id.strategy
    #         old_strategy = 'biggest_tax' if existing_cash_rounding_line.tax_line_id else 'add_invoice_line'
    #         if strategy != old_strategy:
    #             self.line_ids -= existing_cash_rounding_line
    #             existing_cash_rounding_line = self.env['account.move.line']

    #     others_lines = self.line_ids.filtered(lambda line: line.account_id.user_type_id.type not in ('receivable', 'payable'))
    #     others_lines -= existing_cash_rounding_line
    #     total_amount_currency = sum(others_lines.mapped('amount_currency'))

    #     diff_balance, diff_amount_currency = _compute_cash_rounding(self, total_amount_currency)

    #     # The invoice is already rounded.
    #     if self.currency_id.is_zero(diff_balance) and self.currency_id.is_zero(diff_amount_currency):
    #         self.line_ids -= existing_cash_rounding_line
    #         return

    #     _apply_cash_rounding(self, diff_balance, diff_amount_currency, existing_cash_rounding_line)

    # def _inverse_amount_total(self):
    #     for move in self:
    #         if len(move.line_ids) != 2 or move.is_invoice(include_receipts=True):
    #             continue

    #         to_write = []

    #         amount_currency = abs(move.amount_total)
    #         balance = move.currency_id._convert(amount_currency, move.company_currency_id, move.company_id, move.date)

    #         for line in move.line_ids:
    #             if not line.currency_id.is_zero(balance - abs(line.balance)):
    #                 to_write.append((1, line.id, {
    #                     'debit': line.balance > 0.0 and balance or 0.0,
    #                     'credit': line.balance < 0.0 and balance or 0.0,
    #                     'amount_currency': line.balance > 0.0 and amount_currency or -amount_currency,
    #                 }))

    #         move.write({'line_ids': to_write})

    # def _compute_payments_widget_to_reconcile_info(self):
    #     for move in self:
    #         move.invoice_outstanding_credits_debits_widget = json.dumps(False)
    #         move.invoice_has_outstanding = False

    #         if move.state != 'posted' \
    #                 or move.payment_state not in ('not_paid', 'partial') \
    #                 or not move.is_invoice(include_receipts=True):
    #             continue

    #         pay_term_lines = move.line_ids\
    #             .filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))

    #         domain = [
    #             ('account_id', 'in', pay_term_lines.account_id.ids),
    #             ('parent_state', '=', 'posted'),
    #             ('partner_id', '=', move.commercial_partner_id.id),
    #             ('reconciled', '=', False),
    #             '|', ('amount_residual', '!=', 0.0), ('amount_residual_currency', '!=', 0.0),
    #         ]

    #         payments_widget_vals = {'outstanding': True, 'content': [], 'move_id': move.id}

    #         if move.is_inbound():
    #             domain.append(('balance', '<', 0.0))
    #             payments_widget_vals['title'] = _('Outstanding credits')
    #         else:
    #             domain.append(('balance', '>', 0.0))
    #             payments_widget_vals['title'] = _('Outstanding debits')

    #         for line in self.env['account.move.line'].search(domain):

    #             if line.currency_id == move.currency_id:
    #                 # Same foreign currency.
    #                 amount = abs(line.amount_residual_currency)
    #             else:
    #                 # Different foreign currencies.
    #                 amount = move.company_currency_id._convert(
    #                     abs(line.amount_residual),
    #                     move.currency_id,
    #                     move.company_id,
    #                     line.date,
    #                 )

    #             if move.currency_id.is_zero(amount):
    #                 continue

    #             payments_widget_vals['content'].append({
    #                 'journal_name': line.ref or line.move_id.name,
    #                 'amount': amount,
    #                 'currency': move.currency_id.symbol,
    #                 'id': line.id,
    #                 'move_id': line.move_id.id,
    #                 'position': move.currency_id.position,
    #                 'digits': [69, move.currency_id.decimal_places],
    #                 'date': fields.Date.to_string(line.date),
    #                 'account_payment_id': line.payment_id.id,
    #             })

    #         if not payments_widget_vals['content']:
    #             continue

    #         move.invoice_outstanding_credits_debits_widget = json.dumps(payments_widget_vals)
    #         move.invoice_has_outstanding = True
