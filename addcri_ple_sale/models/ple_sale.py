from odoo import fields, models, api
from ..reports.sale_report_xlsx import SaleReportXlsx
from ..reports.sale_report_txt import SaleReportTxt
from ..reports.sale_report import SaleReport
import base64
import json


class PleSale(models.Model):
    _name = 'ple.sale'
    _description = 'ple.sale'
    _inherit = 'ple.base'

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

    def _get_name(self, vals):
        name = 'RV_' + super(PleSale, self)._get_name(vals)
        return name

    def write(self, vals):
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
        self.create_report(vals, model=self._name)
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
        ])
        row = 1
        records = []
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

            taxes_values = list(json.loads(invoice.tax_totals_json).get('groups_by_subtotal', {}).values())
            taxes = taxes_values and taxes_values[0] or []

            # ! test
            inv_lines = invoice.invoice_line_ids
            tax_groups = inv_lines.tax_ids.tax_group_id
            amount_total_taxes = tax_groups.mapped(lambda gt: (gt.name, sum(inv_lines.filtered(lambda il: gt in il.tax_ids.tax_group_id).mapped(lambda il: il.price_subtotal))))
            amount_total_taxes = dict(amount_total_taxes)

            # !
            exchange_rate = invoice.exchange_rate

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
                'amount_untaxed': amount_total_taxes.get('IGV', 0)*exchange_rate,  # ! invoice.currency_id._convert(invoice.amount_untaxed, self.env.user.company_id.currency_id, self.env.user.company_id, invoice.date, round=True),  # ! invoice.amount_untaxed,  # sum_amount_untaxed,
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
                # 'ple_sale_id': self.id,
                'journal_name': invoice.journal_id.code,
                'document_code': invoice.l10n_latam_document_type_id.code,
                'ref': invoice.ref,
                # * me
                'sale_move_period': invoice.sale_move_period,
                'exchange_inconsistent': invoice.exchange_inconsistent,
                'cancel_with_payment_method': invoice.cancel_with_payment_method,
                # * taxes
                'tax_exp': amount_total_taxes.get('EXP', 0)*exchange_rate,
                'tax_ina': amount_total_taxes.get('INA', 0)*exchange_rate,
                'tax_exo': amount_total_taxes.get('EXO', 0)*exchange_rate,
                # 'tax_icbp': amount_total_taxes.get('ICBP', 0)*exchange_rate,
                # 'tax_exp': self._get_amount_tax(taxes, 'EXP')*exchange_rate,
                # 'tax_ina': self._get_amount_tax(taxes, 'INA')*exchange_rate,
                # 'tax_exo': self._get_amount_tax(taxes, 'EXO')*exchange_rate,
                'tax_icbp': self._get_amount_tax(taxes, 'ICBP')*exchange_rate  # ! sin tipo de cambio ya que en la factura esto es un nùmero que representa ya el valor en soles *exchange_rate,
            }
            records.append((0, 0, values))
            row += 1
        self.line_ids = records
        return self.action_generate_report()

    def _get_amount_tax(self, values, tax):
        arr_tax = list(filter(lambda t: t.get('tax_group_name', '') == tax, values))
        return dict(arr_tax and arr_tax[-1] or {}).get('tax_group_amount', 0)

    # def _get_amount_tax(self, values, tax):
    #     arr_tax = list(filter(lambda t: t.get('tax_group_name', '') == tax, values))
    #     return dict(arr_tax and arr_tax[-1] or {}).get('tax_group_amount', 0)

    def get_data(self):
        data = []
        for line in self.line_ids:
            value = {
                'period': line.name,
                'number_origin': line.number_origin,
                'journal_correlative': line.journal_correlative,
                'date_invoice': line.date_invoice and line.date_invoice.strftime('%d/%m/%Y') or '',
                'date_due': line.date_due and line.date_due.strftime('%d/%m/%Y') or '',
                'voucher_sunat_code': line.voucher_sunat_code,
                'voucher_series': line.series,
                'correlative': line.correlative,
                'correlative_end': line.correlative_end,
                'customer_document_type': line.customer_document_type,
                'customer_document_number': line.customer_document_number,
                'customer_name': line.customer_name,
                'amount_export': line.amount_export,
                'amount_untaxed': line.amount_untaxed,
                'discount_tax_base': line.discount_tax_base,
                'sale_no_gravadas_igv': line.sale_no_gravadas_igv,
                'discount_igv': line.discount_igv,
                'amount_exonerated': line.amount_exonerated,
                'amount_no_effect': line.amount_no_effect,
                'isc': line.isc,
                'rice_tax_base': line.rice_tax_base or '',
                'rice_igv': line.rice_igv or '',
                'another_taxes': line.another_taxes,
                'amount_total': line.amount_total,
                'code_currency': line.code_currency,
                'currency_rate': line.currency_rate,
                'origin_date_invoice': line.origin_date_invoice and line.origin_date_invoice.strftime('%d/%m/%Y') or '',
                'origin_document_code': line.origin_document_code,
                'origin_serie': line.origin_serie,
                'origin_correlative': line.origin_correlative,
                'contract_name': line.contract_name,
                'inconsistency_type_change': line.inconsistency_type_change,
                'payment_voucher': line.payment_voucher,
                'ple_state': line.ple_state,
                ####
                'journal_name': line.journal_name,
                'document_code': line.document_code,
                # * me
                'sale_move_period': line.sale_move_period,
                'exchange_inconsistent': line.exchange_inconsistent,
                'cancel_with_payment_method': line.cancel_with_payment_method,
                # * TAX
                'tax_exp': line.tax_exp,
                'tax_ina': line.tax_ina,
                'tax_exo': line.tax_exo,
                'tax_icbp': line.tax_icbp,
            }
            data.append(value)
        return data

    def action_generate_report(self):
        data = self.get_data()
        data = SaleReport(data)._get_data()
        sale_report = SaleReportTxt(self, data)
        values_content = sale_report.get_content()
        self.txt_binary = base64.b64encode(
            values_content.encode() or '\n'.encode()
        )
        period_month = dict(self._fields.get('period_month').selection).get(self.period_month)
        self.txt_filename = sale_report.get_filename()
        if not values_content:
            self.error_dialog = 'No hay contenido para presentar en el registro de ventas electrónicos de este periodo.'
        else:
            self.error_dialog = ''

        sale_report_xls = SaleReportXlsx(self, data)
        values_content_xls = sale_report_xls.get_content()
        self.xlsx_binary = base64.b64encode(values_content_xls)
        self.xlsx_filename = sale_report_xls.get_filename(self.period_year, period_month, self.company_id.name)
        self.datetime_ple = fields.Datetime.now()
        # self.state = 'load'
        return True

    @api.model
    def create(self, vals):
        res = super(PleSale, self).create(vals)
        res.create_report(vals, model=self._name)
        return res

    def unlink(self):
        for record in self:
            record.delete_old_record(model=self._name)
        return super(PleSale, self).unlink()
