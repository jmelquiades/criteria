class SaleReport(object):
    def __init__(self, data):
        self.data_14_1 = self.get_data_14_1(data)
        self.data_14_2 = self.get_data_14_2(data)

    def get_data_14_1(self, data):
        data_14_1 = []
        for value in data:
            record = {
                'field_1': value['period'],
                'field_2': value['period'].replace('00', '') + value['journal_name'] + value['voucher_series'] + '-' + value['correlative'].zfill(8),
                'field_3':  'M'+value['correlative'].zfill(8),
                'field_4': value['date_invoice'],
                'field_5': '',
                'field_6': value['document_code'] or '',
                'field_7': value['voucher_series'] or '0000',
                'field_8': value['correlative'].zfill(8) or '',
                'field_9': '',
                'field_10':  value['customer_document_type'] or '',
                'field_11': value['customer_document_number'] or '',
                'field_12': value['customer_name'] or '',
                'field_13': '0.00',
                'field_14':  '%.2f' % value['amount_untaxed'],
                'field_15': '0.00',
                'field_16': '%.2f' % (value['amount_total'] - value['amount_untaxed']),  # value['tax_totals_json'],
                'field_17': '0.00',
                'field_18': '0.00',
                'field_19': '0.00',
                'field_20':  '0.00',
                'field_21': '0.00',
                'field_22': '0.00',
                'field_23': '0.00',
                'field_24': '0.00',
                'field_25': '%.2f' % value['amount_total'],
                'field_26': value['code_currency'],
                'field_27': '%.3f' % value['currency_rate'],
                'field_28': value['origin_date_invoice'] if value['document_code'] in ['07', '08', '87', '88'] and 1 == 1 else '',  # '',
                'field_29': value['origin_document_code'] if value['document_code'] in ['07', '08', '87', '88'] and 1 == 1 else '',  # '',
                'field_30':  value['origin_serie'] if value['document_code'] in ['07', '08', '87', '88'] and 1 == 1 else '',  # '',
                'field_31': value['origin_correlative'] if value['document_code'] in ['07', '08', '87', '88'] and 1 == 1 else '',  # '',
                'field_32': '',
                'field_33': '',
                'field_34': '',
                'field_35':  '1',
                'field_36': ''
            }
            data_14_1.append(record)
        return data_14_1

    def get_data_14_2(self, data):
        return []

    def _get_data(self):
        return [self.data_14_1, self.data_14_2]
