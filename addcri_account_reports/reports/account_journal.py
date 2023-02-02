
import time
from odoo import api, models, _
from odoo.exceptions import UserError


class ReportJournal(models.AbstractModel):
    _name = 'report.addcri_account_reports.report_journal_l10n_pe'
    _inherit = 'report.account.report_journal'
    _description = 'Account Journal Report'