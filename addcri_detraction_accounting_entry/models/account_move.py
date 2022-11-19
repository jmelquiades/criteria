from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'
    _description = 'Account Move'

    def _recompute_dynamic_lines(self, recompute_all_taxes=False, recompute_tax_base_amount=False):
        super(AccountMove, self)._recompute_dynamic_lines(recompute_all_taxes, recompute_tax_base_amount)
        self.add_line_detraction()

    # def _onchange_detraction_percent(self):
    #     super(AccountMove, self)._onchange_detraction_percent()
    #     if self.line_ids:
    #         self._recompute_dynamic_lines()

    def add_line_detraction(self):
        if not self.company_id.detraction_outbound_account_id:
            raise UserError('Configurar cuenta para pago de detracciones.')

        detraction_outbound_account = self.company_id.detraction_outbound_account_id
        if self.l10n_pe_dte_is_detraction and self.state == 'draft':
            merc = self.line_ids.filtered(lambda line: line.exclude_from_invoice_tab and line.account_id == detraction_outbound_account)

            if len(merc) > 1:
                raise UserError('Hay más de un apunte contable con la cuenta de pago de detracciones.')

            balance = self.l10n_pe_dte_detraction_amount
            if not merc:
                values = {
                    'account_id': detraction_outbound_account.id,
                    'balance': balance,
                    'debit': 0.0,
                    'credit': balance,
                    'exclude_from_invoice_tab': True,
                    'move_id': self.id
                }
                self.env['account.move.line'].new(values)
                line_credit = self.line_ids.filtered(lambda line: line.exclude_from_invoice_tab and line.account_id != detraction_outbound_account and line.credit > 0)
                line_credit.credit -= balance
                line_credit._onchange_credit()
                print('script')
            else:
                merc.balance = balance
                merc.credit = balance
                line_credit = self.line_ids.filtered(lambda line: line.exclude_from_invoice_tab and line.account_id != detraction_outbound_account and line.credit > 0)
                line_credit.credit -= balance
                line_credit._onchange_credit()
