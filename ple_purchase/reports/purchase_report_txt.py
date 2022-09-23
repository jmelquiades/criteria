# -*- coding: utf-8 -*-

from io import BytesIO


class PurchaseReportTxt(object):

    def __init__(self, obj, data):
        self.obj = obj
        # self.data = data
        self.data_8_1, self.data_8_2 = data
        self.exists_data_8_1 = False
        self.exists_data_8_2 = False

    def get_content_8_1(self):
        raw = ''
        # template = '{period}|{number_origin}|{journal_correlative}|'\
        #            '{date_invoice}|{date_due}|{voucher_sunat_code}|'\
        #            '{voucher_series}|{voucher_year_dua_dsi}|{correlative}|'\
        #            '|{customer_document_type}|{customer_document_number}|'\
        #            '{customer_name}|{base_gdg}|{tax_gdg}|{base_gdm}|{tax_gdm}|' \
        #            '{base_gdng}|{tax_gdng}|{amount_untaxed}|' \
        #            '{isc}|{another_taxes}|{amount_total}|' \
        #            '{currency_id}|{invoice_exchange_rate}|' \
        #            '{amendment_invoice_date_invoice}|' \
        #            '{amendment_invoice_document_type_sunat_code}|' \
        #            '{amendment_invoice_voucher_series}|{amendment_code_aduana}|{amendment_invoice_number}|' \
        #            '{constancia_deposito_detraccion_fecha_emision}|{constancia_deposito_detraccion_numero}|' \
        #            '{retention}|{class_good_services}|{irregular_societies}|{error_exchange_rate}|' \
        #            '{supplier_not_found}|{suppliers_resigned}|{dni_ruc}|' \
        #            '{pay_invoice_type}|{ple_state}|\r\n'

        template = '{field_1}|{field_2}|' \
            '{field_3}|{field_4}|{field_5}|' \
            '{field_6}|{field_7}|{field_8}|' \
                   '{field_9}|{field_10}|{field_11}|' \
                   '{field_12}|{field_13}|{field_14}|'  \
                   '{field_15}|{field_16}|{field_17}|' \
                   '{field_18}|{field_19}|{field_20}|{field_21}|' \
                   '{field_22}|{field_23}|{field_24}|' \
                   '{field_25}|{field_26}|{field_27}|' \
                   '{field_28}|{field_29}|' \
                   '{field_30}|{field_31}|' \
                   '{field_32}|{field_33}|{field_34}|' \
                   '{field_35}|{field_36}|{field_37}|' \
            '{field_38}|{field_39}|{field_40}|' \
            '{field_41}|{field_42}|{field_43}\r\n'

        # for value in self.data:
        for value in self.data_8_1:
            # if value['voucher_sunat_code'] not in ['91', '97', '98']:
            # raw += template.format(
            #     period=value['period'],
            #     number_origin=value['number_origin'],
            #     journal_correlative=value['journal_correlative'],
            #     date_invoice=value['date_invoice'],
            #     date_due=value['date_due'],
            #     voucher_sunat_code=value['voucher_sunat_code'] or '',
            #     voucher_series=value['voucher_series'] or '0000',
            #     voucher_year_dua_dsi=value['voucher_year_dua_dsi'] or '',
            #     correlative=value['correlative'] or '',
            #     customer_document_type=value['customer_document_type'] or '',
            #     customer_document_number=value['customer_document_number'] or '',
            #     customer_name=value['customer_name'] or '',
            #     base_gdg='%.2f' % value['base_gdg'],
            #     tax_gdg='%.2f' % value['tax_gdg'],
            #     base_gdm='%.2f' % value['base_gdm'],
            #     tax_gdm='%.2f' % value['tax_gdm'],
            #     base_gdng='%.2f' % value['base_gdng'],
            #     tax_gdng='%.2f' % value['tax_gdng'],
            #     amount_untaxed='%.2f' % value['amount_untaxed'],
            #     isc='%.2f' % value['isc'],
            #     another_taxes='%.2f' % value['another_taxes'],
            #     amount_total='%.2f' % value['amount_total'],
            #     currency_id=value['code_currency'],
            #     invoice_exchange_rate='%.3f' % value['currency_rate'],
            #     amendment_invoice_date_invoice=value['origin_date_invoice'],
            #     amendment_invoice_document_type_sunat_code=value['origin_document_code'] or '',
            #     amendment_invoice_voucher_series=value['origin_serie'] or '',
            #     amendment_code_aduana=value['origin_code_aduana'] or '',
            #     amendment_invoice_number=value['origin_correlative'] or '',
            #     constancia_deposito_detraccion_fecha_emision=value['voucher_date'] or '',
            #     constancia_deposito_detraccion_numero=value['voucher_number'] or '',
            #     retention=value['retention'] or '',
            #     class_good_services=value['class_good_services'] or '',
            #     irregular_societies=value['irregular_societies'] or '',
            #     error_exchange_rate=value['error_exchange_rate'] or '',
            #     supplier_not_found=value['supplier_not_found'] or '',
            #     suppliers_resigned=value['suppliers_resigned'] or '',
            #     dni_ruc=value['dni_ruc'] or '',
            #     pay_invoice_type=value['type_pay_invoice'] or '',
            #     ple_state=value['ple_state'] or ''
            # )
            # raw += template.format(
            #     c1=value['period'],
            #     c2=value['period'].replace('00', '') + value['journal_name'] + value['voucher_series'] + '-' + value['correlative'].zfill(8),
            #     c3='M'+value['correlative'].zfill(8),
            #     c4=value['date_invoice'],
            #     c5=value['date_due'] if value['document_code'] == '14' else '',  # '',
            #     c6=value['document_code'] or '',
            #     c7=value['voucher_series'] or '0000',
            #     c8='0',
            #     c9=value['correlative'].zfill(8) or '',
            #     c10='',
            #     c11=value['customer_document_type'] or '',
            #     c12=value['customer_document_number'] or '',
            #     c13=value['customer_name'] or '',
            #     c14='%.2f' % value['amount_untaxed'],
            #     c15='%.2f' % (value['amount_total'] - value['amount_untaxed']),
            #     c16='0.00',
            #     c17='0.00',
            #     c18='0.00',
            #     c19='0.00',
            #     c20='0.00',
            #     c21='0.00',
            #     c22='0.00',
            #     c23='0.00',
            #     c24='%.2f' % value['amount_total'],
            #     c25=value['code_currency'],
            #     c26='%.3f' % value['currency_rate'],  # value['code_currency'],
            #     c27=value['origin_date_invoice'],  # '',
            #     c28='00',
            #     c29='-',
            #     c30='',
            #     c31='-',
            #     c32='01/01/0001',  # * fecha de retencion
            #     c33='0',
            #     c34='',
            #     c35='',  # or 0
            #     c36='',
            #     c37='',
            #     c38='',
            #     c39='',
            #     c40='',
            #     c41='',
            #     c42='1',
            #     c43=''
            # )
            raw += template.format(**value)
        if raw:
            self.exists_data_8_1 = True
        return raw

    def get_content_8_2(self):
        raw = ''
        # template = '{period}|{number_origin}|{journal_correlative}|' \
        #            '{date_invoice}|{voucher_sunat_code}|{voucher_series}|' \
        #            '{correlative}|{amount_untaxed}|{another_taxes}|' \
        #            '{amount_total}|{amendment_invoice_document_type_sunat_code}|{amendment_invoice_voucher_series}|' \
        #            '{amendment_year_aduana}|{amendment_invoice_number}|{amendment_invoice_retention_igv}|' \
        #            '{currency_id}|{invoice_exchange_rate}|{country_code}|' \
        #            '{customer_name}|{partner_street}|{customer_document_number}||||' \
        #            '{link_partner_beneficiary}|{hard_rent}|{deduccion}|' \
        #            '{rent_neta}|{retention_rate}|{retention_tax}|' \
        #            '{code_double_taxation_agreement}|{exoneration_nodomicilied}|{type_rent}|' \
        #            '{service_taken}|{pre_pay}|{ple_state}|\r\n'
        template = '{field_1}|{field_2}|' \
            '{field_3}|{field_4}|{field_5}|' \
            '{field_6}|{field_7}|{field_8}|' \
                   '{field_9}|{field_10}|{field_11}|' \
                   '{field_12}|{field_13}|{field_14}|'  \
                   '{field_15}|{field_16}|{field_17}|' \
                   '{field_18}|{field_19}|{field_20}|{field_21}|' \
                   '{field_22}|{field_23}|{field_24}|' \
                   '{field_25}|{field_26}|{field_27}|' \
                   '{field_28}|{field_29}|' \
                   '{field_30}|{field_31}|' \
                   '{field_32}|{field_33}\r\n'

        for value in self.data_8_2:
            raw += template.format(**value)
        if raw:
            self.exists_data_8_2 = True
        return raw

    def get_filename_8_1(self, type='01'):
        year, month = self.obj.date_start.strftime('%Y/%m').split('/')
        return 'LE{vat}{period_year}{period_month}0008{type}00001{has_info}{currency}1.txt'.format(
            vat=self.obj.company_id.vat,
            period_year=year,
            period_month=month,
            type=type,
            currency='1' if self.obj.company_id.currency_id.name == 'PEN' else '2',
            has_info=int(bool(self.exists_data_8_1))
        )

    def get_filename_8_2(self):
        year, month = self.obj.date_start.strftime('%Y/%m').split('/')
        return 'LE{vat}{period_year}{period_month}00080200001{has_info}{currency}1.txt'.format(
            vat=self.obj.company_id.vat,
            period_year=year,
            period_month=month,
            currency='1' if self.obj.company_id.currency_id.name == 'PEN' else '2',
            has_info=int(bool(self.exists_data_8_2))
        )
