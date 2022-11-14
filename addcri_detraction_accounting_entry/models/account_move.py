from odoo import _, api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'
    _description = 'Account Move'

    def _recompute_tax_lines(self, recompute_tax_base_amount=False, tax_rep_lines_to_recompute=None):
        super(AccountMove, self)._recompute_tax_lines(recompute_tax_base_amount, tax_rep_lines_to_recompute)
        merc = self.line_ids.filtered(lambda line: not line.exclude_from_invoice_tab)
        for m in merc:
            balance = m.balance
            m.update(
                {
                    'debit': balance > 0.0 and balance - 20 or 0.0,
                    'credit': balance < 0.0 and -balance + 20 or 0.0
                }
            )
        balance = 20
        values = {
            'account_id': self.company_id.detraction_outbound_account_id.id,
            'balance': balance,
            'debit': balance > 0.0 and balance or 0.0,
            'credit': balance < 0.0 and -balance or 0.0,
            'exclude_from_invoice_tab': True
        }
        self.line_ids = [(0, 0, values)]
