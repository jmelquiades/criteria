from odoo import _, api, fields, models
from odoo.exceptions import UserError
import logging


_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'
    _description = 'Account Move'

    def _recompute_dynamic_lines(self, recompute_all_taxes=False, recompute_tax_base_amount=False):
        super(AccountMove, self)._recompute_dynamic_lines(recompute_all_taxes, recompute_tax_base_amount)
        self.add_line_detraction()

    @api.onchange('l10n_pe_dte_detraction_percent', 'currency_id', 'exchange_rate', 'invoice_line_ids')
    def onchange_detraction_percent(self):
        super(AccountMove, self).onchange_detraction_percent()
        for record in self:
            if record != record._origin:
                detraction_outbound_account = record.company_id.detraction_outbound_account_id
                merc = record.line_ids.filtered(lambda line: line.exclude_from_invoice_tab and line.account_id == detraction_outbound_account)
                if merc:
                    record.line_ids -= merc
                record._onchange_invoice_line_ids()

    def add_line_detraction(self):
        if not self.company_id.detraction_outbound_account_id:
            raise UserError('Configurar cuenta para pago de detracciones.')

        detraction_outbound_account = self.company_id.detraction_outbound_account_id
        line_credit = self.line_ids.filtered(lambda line: line.exclude_from_invoice_tab and line.account_id != detraction_outbound_account and line.credit > 0)
        if self.l10n_pe_dte_is_detraction and self.state == 'draft' and self.line_ids and self.move_type == 'in_invoice' and self.l10n_pe_dte_detraction_amount and line_credit:
            merc = self.line_ids.filtered(lambda line: line.exclude_from_invoice_tab and line.account_id == detraction_outbound_account)
            if len(merc) > 1:
                raise UserError('Hay más de un apunte contable con la cuenta de pago de detracciones.')

            balance = self.l10n_pe_dte_detraction_amount
            
            if hasattr(self.company_currency_id, '_convert_sale'):
                amount_currency = -1 * self.company_currency_id._convert_sale(balance, self.currency_id, self.company_id, fields.Date.today(), exchange_rate=1/self.exchange_rate)
            else:
                amount_currency = -1 * self.company_currency_id._convert(balance, self.currency_id, self.company_id, fields.Date.today())
            if not merc:
                values = {
                    'account_id': detraction_outbound_account.id,
                    'balance': balance,
                    'debit': 0.0,
                    'credit': balance,
                    'amount_currency': amount_currency,
                    'price_unit': -1 * balance,
                    'exclude_from_invoice_tab': True,
                    'move_id': self.id,
                    'currency_id': self.currency_id.id
                }
                self.env['account.move.line'].new(values)
            else:
                merc.balance = balance
                merc.credit = balance
                merc.currency_id = self.currency_id.id

            if line_credit:
                line_credit.credit -= balance
                line_credit.amount_currency -= amount_currency
                line_credit.price_unit += balance
                line_credit._onchange_credit()
                line_credit._get_fields_onchange_balance()

            # Only synchronize one2many in onchange.
            if self != self._origin:
                self.invoice_line_ids = self.line_ids.filtered(lambda line: not line.exclude_from_invoice_tab)

