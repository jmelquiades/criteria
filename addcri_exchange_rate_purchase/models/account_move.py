from odoo import _, api, fields, models
import logging
import json

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
        lines = (self.line_ids | self.invoice_line_ids)
        lines._onchange_price_subtotal()


    def _recompute_dynamic_lines(self, recompute_all_taxes=False, recompute_tax_base_amount=False):
        super(AccountMove, self)._recompute_dynamic_lines(recompute_all_taxes, recompute_tax_base_amount)
        self._onchange_price_subtotal_from_exchange_rate()

    def _compute_payments_widget_to_reconcile_info(self):
        for move in self:
            move.invoice_outstanding_credits_debits_widget = json.dumps(False)
            move.invoice_has_outstanding = False

            if move.state != 'posted' \
                    or move.payment_state not in ('not_paid', 'partial') \
                    or not move.is_invoice(include_receipts=True):
                continue

            pay_term_lines = move.line_ids\
                .filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))

            domain = [
                ('account_id', 'in', pay_term_lines.account_id.ids),
                ('parent_state', '=', 'posted'),
                ('partner_id', '=', move.commercial_partner_id.id),
                ('reconciled', '=', False),
                '|', ('amount_residual', '!=', 0.0), ('amount_residual_currency', '!=', 0.0),
            ]

            payments_widget_vals = {'outstanding': True, 'content': [], 'move_id': move.id}

            if move.is_inbound():
                domain.append(('balance', '<', 0.0))
                payments_widget_vals['title'] = _('Outstanding credits')
            else:
                domain.append(('balance', '>', 0.0))
                payments_widget_vals['title'] = _('Outstanding debits')

            for line in self.env['account.move.line'].search(domain):

                if line.move_id.payment_id.payment_type == 'inbound':
                    convert = getattr(move.company_currency_id, '_convert_purchase')
                elif line.move_id.payment_id.payment_type == 'outbound':
                    convert = getattr(move.company_currency_id, '_convert_sale')
                else:
                    convert = getattr(move.company_currency_id, '_convert')

                if line.currency_id == move.currency_id:
                    # Same foreign currency.
                    amount = abs(line.amount_residual_currency)
                else:
                    # Different foreign currencies.
                    amount = convert(
                        abs(line.amount_residual),
                        move.currency_id,
                        move.company_id,
                        line.date,
                    )

                if move.currency_id.is_zero(amount):
                    continue

                payments_widget_vals['content'].append({
                    'journal_name': line.ref or line.move_id.name,
                    'amount': amount,
                    'currency': move.currency_id.symbol,
                    'id': line.id,
                    'move_id': line.move_id.id,
                    'position': move.currency_id.position,
                    'digits': [69, move.currency_id.decimal_places],
                    'date': fields.Date.to_string(line.date),
                    'account_payment_id': line.payment_id.id,
                })

            if not payments_widget_vals['content']:
                continue

            move.invoice_outstanding_credits_debits_widget = json.dumps(payments_widget_vals)
            move.invoice_has_outstanding = True

