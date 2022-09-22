from odoo import fields, models
from ..reports.sale_report_xlsx import SaleReportXlsx
from ..reports.sale_report_txt import SaleReportTxt
import base64


class PleSale(models.Model):
    _name = 'ple.sale'
    # _inherits = {'ple.report.base': 'ple_id'}
    _inherit = 'ple.base'

    # ple_id = fields.Many2one(
    #     comodel_name='ple.report.base',
    #     auto_join=True,
    #     ondelete="cascade",
    #     required=True,
    #     index=True
    # )
    line_ids = fields.One2many(
        comodel_name='ple.sale.line',
        inverse_name='ple_sale_id',
        string='Líneas'
    )
    txt_binary = fields.Binary('Reporte TXT')
    txt_filename = fields.Char()

    xlsx_binary = fields.Binary('Report XLSX')
    xlsx_filename = fields.Char()
    error_dialog = fields.Text('Error dialog')

    # def unlink(self):
    #     unlink_ple_sale = self.env['ple.report.sale']
    #     unlink_ple_base = self.env['ple.base']
    #     for obj in self:
    #         if not obj.exists():
    #             continue
    #         unlink_ple_base |= obj.ple_id
    #         unlink_ple_sale |= obj
    #     res = super(PleReportSale, unlink_ple_sale).unlink()
    #     unlink_ple_base.unlink()
    #     return res

    # def _get_data_invoice(self, invoice):
    #     return self.env['ple.report.base']._get_data_invoice(invoice)

    # def _get_journal_correlative(self, invoice):
    #     obj_company = self.company_id
    #     return self.env['ple.report.base']._get_journal_correlative(obj_company, invoice)

    # def _get_data_origin(self, invoice):
    #     return self.env['ple.report.base']._get_data_origin(invoice)

    # def _get_number_origin(self, invoice):
    #     return self.env['ple.report.base']._get_number_origin(invoice)

    # def _refund_amount(self, invoice):
    #     return self.env['ple.report.base']._refund_amount(invoice)

    def write(self, vals):
        # prop1 = {'date_end', 'date_start', 'company_id'}.intersection(vals.keys())
        prop1 = {'period_month', 'period_year', 'company_id'}.intersection(vals.keys())
        prop2 = vals.get('state', False) == 'draft'
        if prop1 or prop2:
            vals.update({
                'xlsx_binary': False,
                'txt_binary': False,
                'state': 'draft',
            })
        if prop2:
            self.line_ids.unlink()
        return super(PleSale, self).write(vals)

    def _get_tax(self, invoice):
        values = {
            'S_BASE_EXP': 0.0,
            'S_BASE_OG': 0.0,
            'S_BASE_OGD': 0.0,
            'S_TAX_OG': 0.0,
            'S_TAX_OGD': 0.0,
            'S_BASE_OE': 0.0,
            'S_BASE_OU': 0.0,
            'S_TAX_ISC': 0.0,
            'S_BASE_IVAP': 0.0,
            'S_TAX_IVAP': 0.0,
            'S_TAX_OTHER': 0.0,
            'AMOUNT_TOTAL': 0.0
        }

        if invoice.state != 'cancel':
            for obj_ml in invoice.line_ids:
                amount = obj_ml.debit if obj_ml.debit > obj_ml.credit else obj_ml.credit
                for obj_tag_tax in obj_ml.tax_tag_ids:
                    if obj_tag_tax.name[1:] in values:
                        values[obj_tag_tax.name[1:]] += amount
                values['AMOUNT_TOTAL'] += obj_ml.credit

        if invoice.move_type == 'out_refund':
            self._refund_amount(values)
        return values

    def update_data_lines(self):
        self.line_ids.unlink()

        list_invoices = self.env['account.move'].search([
            ('company_id', '=', self.company_id.id),
            ('move_type', 'in', ['out_invoice', 'out_refund']),
            ('date', '>=', self.date_start),
            ('date', '<=', self.date_end),
            ('state', 'not in', ['draft']),
            ('journal_id.no_include_ple', '=', False),
            ('journal_id.type', '=', 'sale'),
            ('its_declared', '=', False),
            # ('document_code', 'in', ['07', '08', '87', '88'])
        ])
        row = 1
        for invoice in list_invoices:
            date_due, ple_state, document_type, document_number, customer_name = self._get_data_invoice(invoice)
            origin_date_invoice, origin_document_code, origin_serie, origin_correlative, _ = self._get_data_origin(invoice)

            v = self._get_tax(invoice)
            sum_amount_export = v['S_BASE_EXP']
            sum_amount_untaxed = v['S_BASE_OG']
            sum_discount_tax_base = v['S_BASE_OGD']
            sum_sale_no_gravadas_igv = v['S_TAX_OG']
            sum_discount_igv = v['S_TAX_OGD']
            sum_amount_exonerated = v['S_BASE_OE']
            sum_amount_no_effect = v['S_BASE_OU']
            sum_isc = v['S_TAX_ISC']
            sum_rice_tax_base = v['S_BASE_IVAP']
            sum_rice_igv = v['S_TAX_IVAP']
            sum_another_taxes = v['S_TAX_OTHER']
            amount_total = v['AMOUNT_TOTAL']

            values = {
                'row': row,
                'name': invoice.date.strftime('%Y%m00'),
                'number_origin': self._get_number_origin(invoice),
                'journal_correlative': self._get_journal_correlative(invoice.company_id),
                'date_invoice': invoice.invoice_date,
                'date': invoice.date,
                'date_due': date_due,
                'voucher_sunat_code': invoice.l10n_latam_document_type_id.sequence,  # invoice.sunat_code,
                'series': invoice.sequence_prefix.split()[-1].replace('-', ''),  # invoice.prefix_val,
                'correlative': invoice.sequence_number,  # invoice.suffix_val,
                'customer_document_type': document_type,
                'customer_document_number': document_number,
                'customer_name': customer_name,
                'amount_export': sum_amount_export,
                'amount_untaxed':  invoice.currency_id._convert(invoice.amount_untaxed, self.env.user.company_id.currency_id, self.env.user.company_id, invoice.date, round=True),  # invoice.amount_untaxed,  # sum_amount_untaxed,
                'discount_tax_base': sum_discount_tax_base,
                'sale_no_gravadas_igv': sum_sale_no_gravadas_igv,
                'discount_igv': sum_discount_igv,
                'amount_exonerated': sum_amount_exonerated,
                'amount_no_effect': sum_amount_no_effect,
                'isc': sum_isc,
                'rice_tax_base': sum_rice_tax_base,
                'rice_igv': sum_rice_igv,
                'another_taxes': sum_another_taxes,
                'amount_taxed': invoice.currency_id._convert(invoice.amount_total - invoice.amount_untaxed, self.env.user.company_id.currency_id, self.env.user.company_id, invoice.date, round=True),
                'amount_total': invoice.currency_id._convert(invoice.amount_total, self.env.user.company_id.currency_id, self.env.user.company_id, invoice.date, round=True),  # amount_total,
                'code_currency': invoice.currency_id.name,
                'currency_rate': round(self.env['res.currency']._get_conversion_rate(invoice.currency_id, self.env.user.company_id.currency_id, self.env.user.company_id, invoice.date), 4),  # invoice_date lo cambié por date # round(invoice.exchange_rate, 3),
                'origin_date_invoice': origin_date_invoice,
                'origin_document_code': origin_document_code,
                'origin_serie': origin_serie,
                'origin_correlative': origin_correlative,
                'ple_state': ple_state,
                'invoice_id': invoice.id,
                'ple_sale_id': self.id,
                ####
                'journal_name': invoice.journal_id.code,
                'document_code': invoice.l10n_latam_document_type_id.code,
                # 'tax_totals_json': invoice.tax_totals_json
                'ref': invoice.ref
            }
            self.env['ple.sale.line'].create(values)
            row += 1
        return self.action_generate_report()

    def action_generate_report(self):
        list_data = []
        for obj_line in self.line_ids:
            value = {
                'period': obj_line.name,
                'number_origin': obj_line.number_origin,
                'journal_correlative': obj_line.journal_correlative,
                'date_invoice': obj_line.date_invoice and obj_line.date_invoice.strftime('%d/%m/%Y') or '',
                'date_due': obj_line.date_due and obj_line.date_due.strftime('%d/%m/%Y') or '',
                'voucher_sunat_code': obj_line.voucher_sunat_code,
                'voucher_series': obj_line.series,
                'correlative': obj_line.correlative,
                'correlative_end': obj_line.correlative_end,
                'customer_document_type': obj_line.customer_document_type,
                'customer_document_number': obj_line.customer_document_number,
                'customer_name': obj_line.customer_name,
                'amount_export': obj_line.amount_export,
                'amount_untaxed': obj_line.amount_untaxed,
                'discount_tax_base': obj_line.discount_tax_base,
                'sale_no_gravadas_igv': obj_line.sale_no_gravadas_igv,
                'discount_igv': obj_line.discount_igv,
                'amount_exonerated': obj_line.amount_exonerated,
                'amount_no_effect': obj_line.amount_no_effect,
                'isc': obj_line.isc,
                'rice_tax_base': obj_line.rice_tax_base or '',
                'rice_igv': obj_line.rice_igv or '',
                'another_taxes': obj_line.another_taxes,
                'amount_total': obj_line.amount_total,
                'code_currency': obj_line.code_currency,
                'currency_rate': obj_line.currency_rate,
                'origin_date_invoice': obj_line.origin_date_invoice and obj_line.origin_date_invoice.strftime('%d/%m/%Y') or '',
                'origin_document_code': obj_line.origin_document_code,
                'origin_serie': obj_line.origin_serie,
                'origin_correlative': obj_line.origin_correlative,
                'contract_name': obj_line.contract_name,
                'inconsistency_type_change': obj_line.inconsistency_type_change,
                'payment_voucher': obj_line.payment_voucher,
                'ple_state': obj_line.ple_state,
                ####
                'journal_name': obj_line.journal_name,
                'document_code': obj_line.document_code
                # 'tax_totals_json': obj_line.tax_totals_json
            }
            list_data.append(value)
        sale_report = SaleReportTxt(self, list_data)
        values_content = sale_report.get_content()
        self.txt_binary = base64.b64encode(
            values_content.encode() or '\n'.encode()
        )
        self.txt_filename = sale_report.get_filename()
        if not values_content:
            self.error_dialog = 'No hay contenido para presentar en el registro de ventas electrónicos de este periodo.'
        else:
            self.error_dialog = ''

        sale_report_xls = SaleReportXlsx(self, list_data)
        values_content_xls = sale_report_xls.get_content()
        self.xlsx_binary = base64.b64encode(values_content_xls)
        self.xlsx_filename = sale_report_xls.get_filename()
        self.date_ple = fields.Datetime.now()
        # self.state = 'load'
        return True

    # def action_close(self):
    #     self.ensure_one()
    #     self.write({
    #         'state': 'closed'
    #     })
    #     for obj_line in self.line_ids:
    #         if obj_line.invoice_id:
    #             obj_line.invoice_id.its_declared = True
    #     return True

    # def action_rollback(self):
    #     for obj_line in self.line_ids:
    #         if obj_line.invoice_id:
    #             obj_line.invoice_id.its_declared = False
    #     self.state = 'draft'
    #     return True
