# -*- coding: utf-8 -*-

from io import BytesIO


class SaleReportTxt(object):

    def __init__(self, obj, data):
        self.obj = obj
        self.data = data

    def get_content(self):
        raw = ''
        # template = '{period}|{number_origin}|' \
        #            '{journal_correlative}|{date_invoice}|{date_due}|' \
        #            '{voucher_sunat_code}|{voucher_series}|{correlative}|' \
        #            '{correlative_end}|{customer_document_type}|{customer_document_number}|' \
        #            '{customer_name}|{amount_export}|{amount_untaxed}|'  \
        #            '{discount_tax_base}|{sale_no_gravadas_igv}|{discount_igv}|' \
        #            '{amount_exonerated}|{amount_no_effect}|{isc}|{rice_tax_base}|' \
        #            '{rice_igv}|{another_taxes}|{amount_total}|' \
        #            '{code_currency}|{currency_rate}|{amendment_invoice_date_invoice}|' \
        #            '{amendment_invoice_voucher_sunat_code}|{amendment_invoice_voucher_series}|' \
        #            '{amendment_invoice_correlative}|{contract_name}|' \
        #            '{inconsistency_type_change}|{payment_voucher}|{ple_state_sale}|\r\n'
        template = '{c1}|{c2}|' \
                   '{c3}|{c4}|{c5}|' \
                   '{c6}|{c7}|{c8}|' \
                   '{c9}|{c10}|{c11}|' \
                   '{c12}|{c13}|{c14}|'  \
                   '{c15}|{c16}|{c17}|' \
                   '{c18}|{c19}|{c20}|{c21}|' \
                   '{c22}|{c23}|{c24}|' \
                   '{c25}|{c26}|{c27}|' \
                   '{c28}|{c29}|' \
                   '{c30}|{c31}|' \
                   '{c32}|{c33}|{c34}|' \
                   '{c35}|{c36}\r\n'

        for value in self.data:
            # raw += template.format(
            #     period=value['period'],
            #     number_origin=value['number_origin'],
            #     journal_correlative=value['journal_correlative'],
            #     date_invoice=value['date_invoice'],
            #     date_due=value['date_due'],
            #     voucher_sunat_code=value['voucher_sunat_code'] or '',
            #     voucher_series=value['voucher_series'] or '0000',
            #     correlative=value['correlative'] or '',
            #     correlative_end=value['correlative_end'] or '',
            #     customer_document_type=value['customer_document_type'] or '',
            #     customer_document_number=value['customer_document_number'] or '',
            #     customer_name=value['customer_name'] or '',
            #     amount_export='%.2f' % value['amount_export'],
            #     amount_untaxed='%.2f' % value['amount_untaxed'],
            #     discount_tax_base='%.2f' % value['discount_tax_base'],
            #     sale_no_gravadas_igv='%.2f' % value['sale_no_gravadas_igv'],
            #     discount_igv='%.2f' % value['discount_igv'],
            #     amount_exonerated='%.2f' % value['amount_exonerated'],
            #     amount_no_effect='%.2f' % value['amount_no_effect'],
            #     isc='%.2f' % value['isc'],
            #     rice_tax_base='%.2f' % value['rice_tax_base'] if value['rice_tax_base'] else '',
            #     rice_igv='%.2f' % value['rice_igv'] if value['rice_igv'] else '',
            #     another_taxes='%.2f' % value['another_taxes'],
            #     amount_total='%.2f' % value['amount_total'],
            #     code_currency=value['code_currency'],
            #     currency_rate='%.3f' % value['currency_rate'],
            #     amendment_invoice_date_invoice=value['origin_date_invoice'],
            #     amendment_invoice_voucher_sunat_code=value['origin_document_code'] or '',
            #     amendment_invoice_voucher_series=value['origin_serie'] or '',
            #     amendment_invoice_correlative=value['origin_correlative'] or '',
            #     contract_name=value['contract_name'] or '',
            #     inconsistency_type_change=value['inconsistency_type_change'] or '',
            #     payment_voucher=value['payment_voucher'] or '',
            #     ple_state_sale=value['ple_state'] or ''
            # )
            raw += template.format(
                c1=value['period'],
                c2=value['period'].replace('00', '') + value['journal_name'] + value['voucher_series'] + '-' + value['correlative'].zfill(8),
                c3='M'+value['correlative'].zfill(8),
                c4=value['date_invoice'],
                c5='',
                c6=value['document_code'] or '',
                c7=value['voucher_series'] or '0000',
                c8=value['correlative'].zfill(8) or '',
                c9='',
                c10=value['customer_document_type'] or '',
                c11=value['customer_document_number'] or '',
                c12=value['customer_name'] or '',
                c13='0.00',
                c14='%.2f' % value['amount_untaxed'],
                c15='0.00',
                c16='%.2f' % (value['amount_total'] - value['amount_untaxed']),  # value['tax_totals_json'],
                c17='0.00',
                c18='0.00',
                c19='0.00',
                c20='0.00',
                c21='0.00',
                c22='0.00',
                c23='0.00',
                c24='0.00',
                c25='%.2f' % value['amount_total'],
                c26=value['code_currency'],
                c27='%.3f' % value['currency_rate'],
                c28='',
                c29='',
                c30='',
                c31='',
                c32='',
                c33='',
                c34='',
                c35='',
                c36=''
            )
        return raw

    def get_filename(self, type='01'):
        year, month = self.obj.date_start.strftime('%Y/%m').split('/')
        # u'LE{vat}{period_year}{period_month}0014{type}0000{state_send}{has_info}{currency}1.txt'
        return u'LE{vat}{period_year}{period_month}0014{type}0000{has_info}{currency}1.txt'.format(
            vat=self.obj.company_id.vat,
            period_year=year,
            period_month=month,
            type=type,
            # state_send=self.obj.state_send or '',
            currency='1' if self.obj.company_id.currency_id.name == 'PEN' else '2',
            has_info=int(bool(self.data))
        )
