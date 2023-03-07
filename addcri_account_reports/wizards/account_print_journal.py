
from odoo import fields, models, _, api
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from odoo.tools.misc import get_lang
class AccountPrintJournal(models.TransientModel):
    _inherit = "account.print.journal"
    _description = "Account Print Journal"

    report_l10n_pe = fields.Boolean('Solo se muestran en vista formulario de vistas de l10n_pe', default=False)
    report_name = fields.Char('Nombre del reporte')
    position_month = fields.Selection(selection=[('01', 'Ene'), ('02', 'Feb'), ('03', 'Mar'), ('04', 'Abr'), ('05', 'May'), ('06', 'Jun'), ('07', 'Jul'), ('08', 'Ago'), ('09', 'Set'), ('10', 'Oct'), ('11', 'Nov'), ('12', 'Dic')], default='01', string='Mes')
    position_year = fields.Selection(selection=[(str(num), str(num)) for num in reversed(range((datetime.now().year) - 2, (datetime.now().year) + 5))], string="Año", default=lambda self: str(datetime.now().year))

    def l10n_report(self, journals=False):
        journal_ids = self.journal_ids.search([]).ids
        report_l10n_pe = True
        report_name = 'Libro Diario'
        record = {
            'target_move': 'posted',
            'sort_selection': 'move_name',
            'report_l10n_pe': report_l10n_pe,
            'journal_ids': [(6, 0, journal_ids)],
            'report_name': report_name,
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
    
    @api.onchange('position_year', 'position_month', 'report_l10n_pe')
    def onchange_date(self):
        if self.report_l10n_pe:
            self.date_from = datetime(int(self.position_year), int(self.position_month), 1, 0,0,0).date()
            self.date_to = self.date_from + relativedelta(months=1) - timedelta(days=1)
    
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
    
    def lines(self, target_move, journal_ids, sort_selection, data):
        if isinstance(journal_ids, int):
            journal_ids = [journal_ids]

        move_state = ['draft', 'posted']
        if target_move == 'posted':
            move_state = ['posted']

        query_get_clause = self._get_query_get_clause(data)
        params = [tuple(move_state), tuple(journal_ids)] + query_get_clause[2]
        query = 'SELECT "account_move_line".id FROM ' + query_get_clause[0] + ', account_move am, account_account acc WHERE "account_move_line".account_id = acc.id AND "account_move_line".move_id=am.id AND am.state IN %s AND "account_move_line".journal_id IN %s AND ' + query_get_clause[1] + ' ORDER BY '
        if sort_selection == 'date':
            query += '"account_move_line".date'
        else:
            query += 'am.name'
        query += ', "account_move_line".move_id, acc.code'
        self.env.cr.execute(query, tuple(params))
        ids = (x[0] for x in self.env.cr.fetchall())
        return self.env['account.move.line'].browse(ids)
    
    def _get_query_get_clause(self, data):
        return self.env['account.move.line'].with_context(data['form'].get('used_context', {}))._query_get()

    def view_invoices(self):
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['date_from', 'date_to', 'journal_ids', 'target_move', 'company_id'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=get_lang(self.env).code)
        data = super(AccountPrintJournal, self).pre_print_report(data)
        amls = self.lines(self.target_move, self.journal_ids.ids, self.sort_selection, data)
        action = {
            'name': _('Moves'),
            'domain': [('id', 'in', amls.ids)],
            'res_model': 'account.move.line',
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
            'views': [(self.env.ref('account.view_move_line_tree').id, 'tree'), (False, 'form')],
            'context': {'group_by': ['journal_id', 'move_id']}
        }
        if len(amls) == 1:
            action.update({'view_mode': 'form', 'res_id': amls.id})
        return action
    
    def check_report(self):
        self.onchange_date()
        return super(AccountPrintJournal, self).check_report()