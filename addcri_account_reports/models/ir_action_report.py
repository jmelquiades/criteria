from odoo import api, fields, models, tools
class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'
    _description = 'Report Action'

    def report_action(self, docids, data=None, config=True):
        """Return an action of type ir.actions.report.

        :param docids: id/ids/browse record of the records to print (if not used, pass an empty list)
        :param data:
        :param bool config:
        :rtype: bytes
        """
        report_action = super(IrActionsReport, self).report_action(docids=docids, data=data, config=config)
        
       
        discard_logo_check = self.env.context.get('discard_logo_check')
        if not(self.env.is_admin() and not self.env.company.external_report_layout_id and config and not discard_logo_check) and data.get('report_name', False) and data.get('report_l10n_pe', False):
            self.name = data.get('report_name')
            # report_action.update({
            # 'report_name': 'addcri_account_reports.action_report_journal_l10n_pe',
            # 'report_file': 'addcri_account_reports.action_report_journal_l10n_pe'
            # })
        return report_action