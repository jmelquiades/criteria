
from odoo import fields, models
from dateutil.relativedelta import relativedelta

class AccountPrintJournal(models.TransientModel):
    _inherit = "account.print.journal"
    _description = "Account Print Journal"

    def l10n_report(self, journals=False):
        date = fields.Date.today()
        date_from = date.replace(day=1)
        date_to = (date + relativedelta(months=1)).replace(day=1)
        journal_ids = self.journal_ids.search([('type', '=', 'sale')]).ids
        record = {
            'target_move': 'posted',
            'sort_selection': 'move_name',
            'date_from': date_from,
            'date_to': date_to,
            'journal_ids': [(6, 0, journal_ids)]
        }
        journal_report = self.create(record)
        return journal_report.check_report()