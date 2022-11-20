
class PurchaseReport(object):
    def __init__(self, data):
        self.data_8_1 = self.get_data_8_1(data)
        self.data_8_2 = self.get_data_8_2(data)

    def get_data_8_1(self, data):
        data_8_1 = []
        for value in data:
            if value['document_code'] not in ['91', '97', '98']:
                record = {
                    'field_1': value['period'],
                    'field_2': value['period'].replace('00', '') + value['journal_name'] + value['voucher_series'] + '-' + value['correlative'].zfill(8),
                    'field_3': 'M'+value['correlative'].zfill(8),
                    'field_4': value['date_invoice'],
                    'field_5': value['date_due'] if value['document_code'] == '14' else '',  # '',
                    'field_6': value['document_code'] or '',
                    'field_7': value['voucher_series'] or '0000',
                    'field_8': '0',
                    'field_9': value['correlative'].zfill(8) or '',
                    'field_10': '',
                    'field_11': value['customer_document_type'] or '',
                    'field_12': value['customer_document_number'] or '',
                    'field_13': value['customer_name'] or '',
                    'field_14': '%.2f' % value['amount_untaxed'],
                    'field_15': '%.2f' % value['amount_taxed'],
                    'field_16': '0.00',
                    'field_17': '0.00',
                    'field_18': '0.00',
                    'field_19': '0.00',
                    'field_20': '0.00',
                    'field_21': '0.00',
                    'field_22': '0.00',
                    'field_23': '0.00',
                    'field_24': '%.2f' % value['amount_total'],
                    'field_25': value['code_currency'],
                    'field_26': '%.3f' % value['currency_rate'],  # value['code_currency'],
                    'field_27': value['origin_date_invoice'],  # '',
                    'field_28': '00',
                    'field_29': '-',
                    'field_30': '',
                    'field_31': '-',
                    'field_32': '01/01/0001',  # * fecha de retencion
                    'field_33': '0',
                    'field_34': '1' if value['l10n_pe_dte_is_retention'] == True else '',
                    'field_35': value['adquisition_type'] if value['purchase_move_period'] else '',
                    'field_36': value['contract_or_project'] or '',
                    'field_37': '1' if value['exchange_inconsistent'] == True else '',
                    'field_38': '1' if value['non_existing_supplier'] == True else '',
                    'field_39': '1' if value['waived_exemption_from_igv'] == True else '',
                    'field_40': '1' if value['vat_inconsistent'] == True else '',
                    'field_41': '1' if value['cancel_with_payment_method'] == True else '',
                    'field_42': value['purchase_move_period'] if value['purchase_move_period'] else '',
                    'field_43': ''
                }
                data_8_1.append(record)
        return data_8_1

    def get_data_8_2(self, data):
        data_8_2 = []
        for value in data:
            if value['document_code'] in ['00', '91', '97', '98'] and value['not_domiciled']:
                record = {
                    'field_1': value['period'],
                    'field_2': value['number_origin'],
                    'field_3': value['journal_correlative'],
                    'field_4':  value['date_invoice'],  # *
                    'field_5': value['voucher_sunat_code'] or '',  # *
                    'field_6': value['voucher_series'] or '0000',
                    'field_7':  value['correlative'] or '',
                    'field_8': '%.2f' % value['amount_untaxed'],
                    'field_9':  '%.2f' % value['another_taxes'],
                    'field_10':  '%.2f' % value['amount_total'],
                    'field_11': value['inv_type_document'] or '',
                    'field_12':  value['inv_serie'] or '',
                    'field_13': value['inv_year_dua_dsi'],
                    'field_14':  value['inv_correlative'] or '',
                    'field_15':  value['inv_retention_igv'] or '',
                    'field_16': value['code_currency'],
                    'field_17':  '%.3f' % value['currency_rate'],
                    'field_18': value['country_code'] or '',
                    'field_19': value['customer_name'] or '',
                    'field_20': value['partner_street'] or '',
                    'field_21': value['customer_document_number'] or '',
                    'field_22': value['linkage_code'] or '',
                    'field_23':  value['hard_rent'],
                    'field_24':  value['deduccion_cost'],
                    'field_25': value['rent_neta'],
                    'field_26':  value['retention_rate'],
                    'field_27': value['tax_withheld'],
                    'field_28':  '',
                    'field_29': value['exoneration_nodomicilied_code'] or '',
                    'field_30':  '',
                    'field_31': value['cdi'] or '',
                    'field_32': value['application_article'] or '',
                    'field_33': value['type_rent_code'] or '',  # *
                    'field_36': value['not_domiciled_purchase_move_period'] or '',  # *
                }
                data_8_2.append(record)
        return data_8_2

    def _get_data(self):
        return [self.data_8_1, self.data_8_2]
