from odoo import _, api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'
    _description = 'Account Move'

    def _recompute_dynamic_lines(self, recompute_all_taxes=False, recompute_tax_base_amount=False):
        super(AccountMove, self)._recompute_dynamic_lines(recompute_all_taxes, recompute_tax_base_amount)
        merc = self.line_ids.filtered(lambda line: not line.exclude_from_invoice_tab)
        # self._inverse_amount_total()
        balance = 20
        values = {
            'account_id': self.company_id.detraction_outbound_account_id.id,
            'balance': balance,
            'debit': balance > 0.0 and balance or 0.0,
            'credit': balance < 0.0 and -balance or 0.0,
            'exclude_from_invoice_tab': True
        }
        self.line_ids = [(0, 0, values)]
        if merc:
            m = merc[0]
        # for m in merc:
            balance = m.balance
            m.update(
                {
                    'debit': balance > 0.0 and balance - 20 or 0.0,
                    'credit': balance < 0.0 and -balance + 20 or 0.0
                }
            )
