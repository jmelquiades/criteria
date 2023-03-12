# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta
class Report_Libro_Mayor(models.TransientModel):
    _name = 'report.libro.mayor'
    _description = "Reporte Libro Mayor"
    _inherit = ['account.general.ledger']

    filter_date = {'mode': 'range', 'filter': 'this_month'}
    filter_all_entries = False
    filter_journals = True
    filter_analytic = True
    filter_unfold_all = False

    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=False, default=lambda self: self.env.company)
    # fiscal_year = fields.Integer(
    #      string='Fiscal year',
    #  )
    date_from = fields.Date(string='Start Date',
    default=datetime.today()
    )
    date_to = fields.Date(string='End Date',
    default=str(datetime.now() + relativedelta(months=+1, day=1, days=-1))[:10])

    @api.onchange('date_from')
    def onchange_date_from(self):
        if self.date_from:
            self.date_to=str(self.date_from + relativedelta(months=+1, day=1, days=-1))[:10]
            a=self._get_report_name()
            print(a)
    
    def get_report(self):
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'company_id': self.company_id.id
        }
        return self.env.ref('addcri_account_report_libro_mayor.action_report_libro_mayor').report_action(self, data=data)

class ReportCard(models.AbstractModel):
    _name = 'report.addcri_account_report_libro_mayor.report_libro_mayor'

    @api.model
    def _get_report_values(self, docids, data=None):
        _data= {
            'doc_ids': docids,
            'doc_model': 'account.move',
            'docs': self.env['account.move'].search_read([('invoice_date', '>=', data['date_from']),
                                                        ('invoice_date', '<=', data['date_to']),
                                                        ('company_id', '=', data['company_id']),
                                                        ],
                                                       ['name', 'invoice_date',
                                                       'voucher_number','amount_total',
                                                       'amount_residual','glosa','Serie_purchase']),
            'data': data,
            'company': self.env.user.company_id,
            'date_from': self.format_date(data['date_from']),
            'date_to': self.format_date(data['date_to'])
        }
        return _data

    def format_date(self, date):
        date_parts = date.split('-')
        return '{}/{}/{}'.format(date_parts[2], date_parts[1], date_parts[0])
