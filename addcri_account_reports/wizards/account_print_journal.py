
from odoo import fields, models
# from dateutil.relativedelta import relativedelta
from odoo.tools.misc import get_lang
class AccountPrintJournal(models.TransientModel):
    _inherit = "account.print.journal"
    _description = "Account Print Journal"

    report_l10n_pe = fields.Boolean('Solo se muestran en vista formulario de vistas de l10n_pe')
    report_name = fields.Char('Nombre del reporte')

    def l10n_report(self, journals=False):
        journal_ids = self.journal_ids.search([]).ids
        report_l10n_pe = True
        report_name = 'Libro Diario'
        record = {
            'target_move': 'posted',
            'sort_selection': 'move_name',
            'report_l10n_pe': report_l10n_pe,
            'journal_ids': [(6, 0, journal_ids)],
            'report_name': report_name
        }
        journal_report = self.create(record)

        view_id = self.env.ref('account_reports.account_report_print_journal_view')
        
        open_view = {
            'name': report_name,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.print.journal',
            'type': 'ir.actions.act_window',
            'res_id': journal_report.id,
            'view_id': view_id.id,
            'target': 'new',
        }

        return open_view
    
    def pre_print_report(self, data):
        data = super(AccountPrintJournal, self).pre_print_report(data)
        if self.report_name and self.report_l10n_pe:
            data['report_name'] = self.report_name
            data['report_l10n_pe'] = self.report_l10n_pe
        return data
    
    def _print_report(self, data):
        if self.report_name and self.report_l10n_pe:
            data = self.pre_print_report(data)
            data['form'].update({'sort_selection': self.sort_selection})
            return self.env.ref('addcri_account_reports.action_report_journal_l10n_pe').with_context(landscape=True).report_action(self, data=data)
        return super(AccountPrintJournal, self)._print_report(data=data)