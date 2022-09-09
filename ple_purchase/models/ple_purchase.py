# -*- coding: utf-8 -*-

from odoo import fields, models
from ..reports.purchase_report_xlsx import PurchaseReportXlsx
from ..reports.purchase_report_txt import PurchaseReportTxt


class PlePurchase(models.Model):
    _name = 'ple.purchase'
    # _inherits = {'ple.report.base': 'ple_id'}
    _inherit = 'ple.base'

    # ple_id = fields.Many2one(
    #     comodel_name='ple.base',
    #     auto_join=True,
    #     ondelete='cascade',
    #     required=True,
    #     index=True
    # )
    line_ids = fields.One2many(
        comodel_name='ple.purchase.line',
        inverse_name='ple_purchase_id',
        string='Líneas'
    )
    xlsx_filename_8_1 = fields.Char()
    xlsx_binary_8_1 = fields.Binary('Reporte XLSX')
    txt_filename_8_1 = fields.Char()
    txt_binary_8_1 = fields.Binary('Reporte TXT')
    xlsx_filename_8_2 = fields.Char()
    xlsx_binary_8_2 = fields.Binary('Reporte XLSX')
    txt_filename_8_2 = fields.Char()
    txt_binary_8_2 = fields.Binary('Reporte TXT')
    error_dialog_8_1 = fields.Text(readonly=True)
    error_dialog_8_2 = fields.Text(readonly=True)

    def action_generate_report(self):
        self.line_ids.unlink()

        list_invoices = self.env['account.move'].search([
            ('company_id', '=', self.company_id.id),
            ('type', 'in', ['in_invoice', 'in_refund']),
            ('date', '>=', self.date_start),
            ('date', '<=', self.date_end),
            ('state', 'not in', ['draft', 'cancel']),
            ('journal_id.no_include_ple', '=', False),
            ('journal_id.type', '=', 'purchase'),
            ('its_declared', '=', False)
        ])
        for invoice in list_invoices:
            date_due, ple_state, document_type, document_number, customer_name = self._get_data_invoice(invoice)
            country_code, is_nodomicilied, partner_street = self._get_partner(invoice)
            origin_date_invoice, origin_document_code, origin_serie, origin_correlative, code_customs_id = self._get_data_origin(invoice)
            v = self._get_tax(invoice)
            sum_base_gdg = v['P_BASE_GDG']
            sum_tax_gdg = v['P_TAX_GDG']
            sum_base_gdm = v['P_BASE_GDM']
            sum_tax_gdm = v['P_TAX_GDM']
            sum_base_gdng = v['P_BASE_GDNG']
            sum_tax_gdng = v['P_TAX_GDNG']
            sum_amount_untaxed = v['P_BASE_NG']
            sum_isc = v['P_TAX_ISC']
            sum_another_taxes = v['P_TAX_OTHER']
            amount_total = v['AMOUNT_TOTAL']

            retention, pay_invoice = self._get_retention(invoice)
            values = {
                'name': invoice.date.strftime('%Y%m00'),
                'number_origin': self._get_number_origin(invoice),  # depende de : ple_state del invoice (campo nuevo en account.move)
                'journal_correlative': self._get_journal_correlative(invoice),  # depende de : type_contributor del invoice (campo nuevo de res.company)
                'date_invoice': invoice.invoice_date,
                'date_due': date_due,
                'voucher_sunat_code': invoice.sunat_code,
                'series': invoice.prefix_val,
                'year_dua_dsi': invoice.year_aduana,
                'correlative': invoice.suffix_val,
                'customer_document_type': document_type,
                'customer_document_number': document_number,
                'customer_name': customer_name,
                'base_gdg': sum_base_gdg,
                'tax_gdg': sum_tax_gdg,
                'base_gdm': sum_base_gdm,
                'tax_gdm': sum_tax_gdm,
                'base_gdng': sum_base_gdng,
                'tax_gdng': sum_tax_gdng,
                'amount_untaxed': sum_amount_untaxed,
                'isc': sum_isc,
                'another_taxes': sum_another_taxes,
                'amount_total': amount_total,
                'code_currency': invoice.currency_id.name,
                'currency_rate': round(invoice.exchange_rate, 3),
                'origin_date_invoice': origin_date_invoice,
                'origin_document_code': origin_document_code,
                'origin_serie': origin_serie,
                'origin_code_aduana': code_customs_id and code_customs_id.code or '',
                'origin_correlative': origin_correlative,
                'voucher_number': invoice.voucher_number,
                'voucher_date': invoice.voucher_payment_date,
                'retention': retention,
                'type_pay_invoice': pay_invoice,
                'country_code': country_code,
                'partner_nodomicilied': is_nodomicilied,
                'ple_state': ple_state,
                'invoice_id': invoice.id,
                'ple_purchase_id': self.id,
                'inv_type_document_code': invoice.inv_type_document.code,
                'inv_serie': invoice.inv_serie,
                'inv_year_dua_dsi': invoice.inv_year_dua_dsi,
                'inv_retention_igv': invoice.inv_retention_igv,
                'inv_correlative': invoice.inv_correlative,
                'partner_street': partner_street,
                'linkage_code': invoice.linkage_id and invoice.linkage_id.code or '',
                'hard_rent': invoice.hard_rent,
                'deduccion_cost': invoice.deduccion_cost,
                'rent_neta': invoice.neto_rent,
                'retention_rate': invoice.retention_rate,
                'tax_withheld': invoice.tax_withheld,
                'cdi': invoice.cdi,
                'exoneration_nodomicilied_code': invoice.exoneration_nodomicilied_id and invoice.exoneration_nodomicilied_id.code or '',
                'type_rent_code': invoice.type_rent_id and invoice.type_rent_id.code or '',
                'taken_code': invoice.taken_id and invoice.taken_id.code or '',
                'application_article': invoice.application_article or ''
            }
            self.env['ple.report.purchase.line'].create(values)
        return True

    def get_data(self):
        data = []
        for line in self.line_ids:
            value = {
                'period': line.name,
                'number_origin': line.number_origin,
                'journal_correlative': line.journal_correlative,
                'date_invoice': line.date_invoice and line.date_invoice.strftime('%d/%m/%Y') or '',
                'date_due': line.date_invoice and line.date_invoice.strftime('%d/%m/%Y') or '',
                'voucher_sunat_code': line.voucher_sunat_code,
                'voucher_series': line.series,
                'voucher_year_dua_dsi': line.year_dua_dsi,
                'correlative': line.correlative,
                'customer_document_type': line.customer_document_type,
                'customer_document_number': line.customer_document_number,
                'customer_name': line.customer_name,
                'base_gdg': line.base_gdg,
                'tax_gdg': line.tax_gdg,
                'base_gdm': line.base_gdm,
                'tax_gdm': line.tax_gdm,
                'base_gdng': line.base_gdng,
                'tax_gdng': line.tax_gdng,
                'amount_untaxed': line.amount_untaxed,
                'isc': line.isc,
                'another_taxes': line.another_taxes,
                'amount_total': line.amount_total,
                'code_currency': line.code_currency,
                'currency_rate': line.currency_rate,
                'origin_date_invoice': line.origin_date_invoice and line.origin_date_invoice.strftime('%d/%m/%Y') or '',
                'origin_document_code': line.origin_document_code,
                'origin_serie': line.origin_serie,
                'origin_code_aduana': line.origin_code_aduana,
                'origin_correlative': line.origin_correlative,
                'voucher_date': line.voucher_date,
                'voucher_number': line.voucher_number,
                'retention': line.retention,
                'class_good_services': line.class_good_services,
                'irregular_societies': line.irregular_societies,
                'error_exchange_rate': line.error_exchange_rate,
                'supplier_not_found': line.supplier_not_found,
                'suppliers_resigned': line.suppliers_resigned,
                'dni_ruc': line.dni_ruc,
                'type_pay_invoice': line.type_pay_invoice,
                'ple_state': line.ple_state,

                'inv_type_document': line.inv_type_document_code,
                'inv_serie': line.inv_serie,
                'inv_year_dua_dsi': line.inv_year_dua_dsi,
                'inv_correlative': line.inv_correlative,
                'inv_retention_igv': line.inv_retention_igv,
                'country_code': line.country_code,
                'partner_street': line.partner_street,
                'linkage_code': line.linkage_code,
                'hard_rent': line.hard_rent,
                'deduccion_cost': line.deduccion_cost,
                'rent_neta': line.rent_neta,
                'retention_rate': line.retention_rate,
                'tax_withheld': line.tax_withheld,
                'cdi': line.cdi,
                'exoneration_nodomicilied_code': line.exoneration_nodomicilied_code,
                'type_rent': line.type_rent_code,
                'taken_code': line.taken_code,
                'application_article': line.application_article,
                'partner_nodomicilied': line.partner_nodomicilied
            }
            data.append(value)
        return data

    def get_reports_txt(self, data):
        # 8.1
        purchase_report_text = PurchaseReportTxt(self, data)
        values_content = purchase_report_text.get_content_8_1()
        if not values_content:
            self.error_dialog_8_1 = 'No hay contenido para presentar en el registro de compras 8.1 electrónicos de este periodo.'
        else:
            self.error_dialog_8_1 = ''
        self.txt_binary_8_1 = base64.b64encode(
            values_content and values_content.encode() or '\n'.encode()
        )
        self.txt_filename_8_1 = purchase_report_text.get_filename_8_1()

        # 8..2

        values_content2 = purchase_report_text.get_content_8_2()
        if not values_content2:
            self.error_dialog_8_2 = 'No hay contenido para presentar en el registro de compreas 8.2 electrónicos de este periodo.'
        else:
            self.error_dialog_8_2 = ''
        self.txt_binary_8_2 = base64.b64encode(
            values_content2 and values_content2.encode() or '\n'.encode()
        )
        self.txt_filename_8_2 = purchase_report_text.get_filename_8_1()

    def get_reports_xlsx(self, data):
        purchase_report_xlsx = PurchaseReportXlsx(self, data)

        # 8.1
        value_content_xlsx_8_1 = purchase_report_xlsx.get_content()
        self.xlsx_binary_8_1 = base64.b64encode(value_content_xlsx_8_1)
        self.xlsx_filename_8_1 = purchase_report_xlsx.get_filename()

        # 8.2
        value_content_xlsx_8_2 = purchase_report_xlsx.get_content('2')
        self.xlsx_binary_8_2 = base64.b64encode(value_content_xlsx_8_2)
        self.xlsx_filename_8_2 = purchase_report_xlsx.get_filename('2')

    def action_generate_report(self):
        data = self.get_data()

        self.get_reports_txt(data)
        self.get_reports_xlsx(data)

        self.date_ple = fields.Date.today()
        self.state = 'load'
        return True

    # def _get_number_origin(self, invoice):
    #     return self.env['ple.report.base']._get_number_origin(invoice)

    # def _get_journal_correlative(self, invoice):
    #     company = self.company_id
    #     return self.env['ple.report.base']._get_journal_correlative(company, invoice)

    # def _get_data_invoice(self, invoice):
    #     return self.env['ple.report.base']._get_data_invoice(invoice)

    # def _get_data_origin(self, invoice):
    #     return self.env['ple.report.base']._get_data_origin(invoice)

    # def _refund_amount(self, invoice):
    #     return self.env['ple.report.base']._refund_amount(invoice)

    def _get_retention(self, invoice):
        retention = invoice.retention_id
        type_pay = invoice.bool_pay_invoice
        return int(bool(retention)) or '', int(type_pay) or ''

    def _get_partner(self, invoice):
        partner = invoice.partner_id
        country_code = partner.country_id.code
        is_nodomicilied = partner.is_nodomicilied
        partner_street = '{} {} {} {} {}'.format(
            partner.country_id.name or '',
            partner.state_id.name or '',
            partner.city or '',
            partner.street or '',
            partner.street2 or ''
        )
        return country_code, is_nodomicilied, partner_street.strip()

    def _get_tax(self, invoice):
        values = {
            'P_BASE_GDG': 0.0,
            'P_TAX_GDG': 0.0,
            'P_BASE_GDM': 0.0,
            'P_TAX_GDM': 0.0,
            'P_BASE_GDNG': 0.0,
            'P_TAX_GDNG': 0.0,
            'P_BASE_NG': 0.0,
            'P_TAX_ISC': 0.0,
            'P_TAX_OTHER': 0.0,
            'AMOUNT_TOTAL': 0.0
        }
        if invoice.state != 'cancel':
            for ml in invoice.line_ids:
                amount = ml.debit if ml.debit > ml.credit else ml.credit
                for tag_tax in ml.tag_ids:
                    if tag_tax.name[1:] in values:
                        values[tag_tax.name[1:]] += amount
                values['AMOUNT_TOTAL'] += ml.debit

        if invoice.type == 'in_refund':
            self._refund_amount(values)
        return values

    def action_close(self):
        self.ensure_one()
        self.write({
            'state': 'closed'
        })
        for line in self.line_ids:
            if line.invoice_id:
                line.invoice_id.its_declared = True
        return True

    def action_rollback(self):
        for line in self.line_ids:
            if line.invoice_id:
                line.invoice_id.its_declared = False
        self.state = 'draft'
        return True
