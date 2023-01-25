
from odoo import fields, models
from dateutil.relativedelta import relativedelta

class AccountPrintJournal(models.TransientModel):
    _inherit = "account.print.journal"
    _description = "Account Print Journal"

    only_form_l10n_pe = fields.Boolean('Solo se muestran en vista formulario de vistas de l10n_pe')

    def l10n_report(self, journals=False):
        date = fields.Date.today()
        # date_from = date.replace(day=1)
        # date_to = (date + relativedelta(months=1)).replace(day=1)
        journal_ids = self.journal_ids.search([]).ids
        only_form_l10n_pe = True
        record = {
            'target_move': 'posted',
            'sort_selection': 'move_name',
            # 'date_from': date_from,
            # 'date_to': date_to,
            'only_form_l10n_pe': only_form_l10n_pe,
            'journal_ids': [(6, 0, journal_ids)]
        }
        journal_report = self.create(record)

        view_id = self.env.ref('account_reports.account_report_print_journal_view')
        
        open_view = {
            'name': 'Libro diario',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.print.journal',
            'type': 'ir.actions.act_window',
            'res_id': journal_report.id,
            'view_id': view_id.id,
            'target': 'new',
        }

        return open_view