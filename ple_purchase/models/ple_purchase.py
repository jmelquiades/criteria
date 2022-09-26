
from odoo import fields, models, api
from ..reports.purchase_report_xlsx import PurchaseReportXlsx
from ..reports.purchase_report_txt import PurchaseReportTxt
from ..reports.purchase_report import PurchaseReport
import base64
from odoo.exceptions import UserError


class PlePurchase(models.Model):
    _name = 'ple.purchase'
    _description = 'ple.purchase'
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

    def _get_name(self, vals):
        name = 'RC_' + super(PlePurchase, self)._get_name(vals)
        return name

    def write(self, vals):
        prop1 = {'period_month', 'period_year', 'company_id'}.intersection(vals.keys())
        prop2 = vals.get('state', False) == 'draft'
        if prop1 or prop2:
            vals.update({
                'xlsx_binary_8_1': False,
                'xlsx_binary_8_2': False,
                'txt_binary_8_1': False,
                'txt_binary_8_2': False,
                'state': 'draft',
            })
        if prop2:
            self.line_ids.unlink()
        self.create_report(vals, model=self._name)
        return super(PlePurchase, self).write(vals)

    def update_data_lines(self):
        self.line_ids.unlink()

        list_invoices = self.env['account.move'].search([
            ('company_id', '=', self.company_id.id),
            ('move_type', 'in', ['in_invoice', 'in_refund']),
            ('date', '>=', self.date_start),
            ('date', '<=', self.date_end),
            ('state', 'not in', ['draft', 'cancel']),
            ('journal_id.no_include_ple', '=', False),
            ('journal_id.type', '=', 'purchase'),
            ('its_declared', '=', False),
            ('l10n_latam_document_type_id.code', '!=', '02')
        ])
        row = 1
        records = []
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
                'row': row,
                'name': invoice.date.strftime('%Y%m00'),
                'number_origin': self._get_number_origin(invoice),  # depende de : ple_state del invoice (campo nuevo en account.move)
                'journal_correlative': self._get_journal_correlative(invoice.company_id),  # depende de : type_contributor del invoice (campo nuevo de res.company)
                'date_invoice': invoice.invoice_date,
                'date': invoice.date,
                'date_due': date_due,
                'voucher_sunat_code': invoice.l10n_latam_document_type_id.sequence,  # invoice.sunat_code,
                'series': invoice.sequence_prefix.split()[-1].replace('-', ''),  # invoice.prefix_val,
                'correlative': invoice.sequence_number,  # invoice.suffix_val,
                'year_dua_dsi': invoice.year_aduana,  # ! creado
                'customer_document_type': document_type,
                'customer_document_number': document_number,
                'customer_name': customer_name,
                'base_gdg': sum_base_gdg,
                'tax_gdg': sum_tax_gdg,
                'base_gdm': sum_base_gdm,
                'tax_gdm': sum_tax_gdm,
                'base_gdng': sum_base_gdng,
                'tax_gdng': sum_tax_gdng,
                'amount_untaxed': invoice.currency_id._convert(invoice.amount_untaxed, self.env.user.company_id.currency_id, self.env.user.company_id, invoice.date, round=True),  # invoice.amount_untaxed,  # sum_amount_untaxed,
                'isc': sum_isc,
                'another_taxes': sum_another_taxes,
                'amount_taxed': invoice.currency_id._convert(invoice.amount_total - invoice.amount_untaxed, self.env.user.company_id.currency_id, self.env.user.company_id, invoice.date, round=True),
                'amount_total': invoice.currency_id._convert(invoice.amount_total, self.env.user.company_id.currency_id, self.env.user.company_id, invoice.date, round=True),  # amount_total,
                'code_currency': invoice.currency_id.name,
                'currency_rate': round(self.env['res.currency']._get_conversion_rate(invoice.currency_id, self.env.user.company_id.currency_id, self.env.user.company_id, invoice.date), 4),  # cambié invoice_date por date  # round(invoice.exchange_rate, 3),
                'origin_date_invoice': origin_date_invoice,
                'origin_document_code': origin_document_code,
                'origin_serie': origin_serie,
                'origin_code_aduana': code_customs_id and code_customs_id.code or '',
                'origin_correlative': origin_correlative,
                'voucher_number': invoice.voucher_number,  # ! creado
                'voucher_date': invoice.voucher_payment_date,
                'retention': retention,
                'type_pay_invoice': pay_invoice,
                'country_code': country_code,
                'partner_nodomicilied': is_nodomicilied,
                'ple_state': ple_state,
                'invoice_id': invoice.id,
                # 'ple_purchase_id': self.id,
                'inv_type_document_code': invoice.l10n_latam_document_type_id.sequence,  # invoice.inv_type_document.code,
                # 'inv_serie': invoice.inv_serie,
                # 'inv_year_dua_dsi': invoice.inv_year_dua_dsi,
                # 'inv_retention_igv': invoice.inv_retention_igv,
                # 'inv_correlative': invoice.inv_correlative,
                'partner_street': partner_street,
                # 'linkage_code': invoice.linkage_id and invoice.linkage_id.code or '',
                # 'hard_rent': invoice.hard_rent,
                # 'deduccion_cost': invoice.deduccion_cost,
                # 'rent_neta': invoice.neto_rent,
                # 'retention_rate': invoice.retention_rate,
                # 'tax_withheld': invoice.tax_withheld,
                # 'cdi': invoice.cdi,
                # 'exoneration_nodomicilied_code': invoice.exoneration_nodomicilied_id and invoice.exoneration_nodomicilied_id.code or '',
                # 'type_rent_code': invoice.type_rent_id and invoice.type_rent_id.code or '',
                # 'taken_code': invoice.taken_id and invoice.taken_id.code or '',
                # 'application_article': invoice.application_article or ''
                ###
                'journal_name': invoice.journal_id.code,
                'document_code': invoice.l10n_latam_document_type_id.code,
                'ref': invoice.ref
            }
            records.append((0, 0, values))
            row += 1
        self.line_ids = records
        return self.action_generate_report()

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
                'partner_nodomicilied': line.partner_nodomicilied,
                'journal_name': line.journal_name,
                'document_code': line.document_code,
                'amount_taxed': line.amount_taxed
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
        period_month = dict(self._fields.get('period_month').selection).get(self.period_month)
        self.xlsx_filename_8_1 = purchase_report_xlsx.get_filename(self.period_year, period_month, self.company_id.name)

        # 8.2
        value_content_xlsx_8_2 = purchase_report_xlsx.get_content('2')
        self.xlsx_binary_8_2 = base64.b64encode(value_content_xlsx_8_2)
        self.xlsx_filename_8_2 = purchase_report_xlsx.get_filename(self.period_year, period_month, self.company_id.name, '2')

    def action_generate_report(self):
        data = self.get_data()
        data = PurchaseReport(data)._get_data()
        if data:
            self.get_reports_txt(data)
            self.get_reports_xlsx(data)

            self.datetime_ple = fields.Datetime.now()
            return True

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
                for tag_tax in ml.tax_tag_ids:  # * tag_ids >> tax_tag_ids
                    if tag_tax.name[1:] in values:
                        values[tag_tax.name[1:]] += amount
                values['AMOUNT_TOTAL'] += ml.debit

        if invoice.move_type == 'in_refund':
            self._refund_amount(values)
        return values

    @api.model
    def create(self, vals):
        res = super(PlePurchase, self).create(vals)
        res.create_report(vals, model=self._name)
        return res

    def unlink(self):
        for record in self:
            record.delete_old_record(model=self._name)
        return super(PlePurchase, self).unlink()
