from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from pytz import timezone
import datetime
import requests
from odoo import _, api, fields, models
import logging
_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = 'res.company'
    _description = 'Res Company'

    @api.model
    def update_rate_currency_after_install(self):
        rslt = True
        active_currencies = self.env['res.currency'].search([])
        if 'PEN' in active_currencies.mapped('name'):
            for (currency_provider, companies) in self.env['res.company'].search([])._group_by_provider().items():
                parse_results = None
                if currency_provider == 'bcrp':
                    parse_function = getattr(companies, '_parse_' + currency_provider + '_update_purchase_data')
                    parse_results = parse_function(active_currencies)

                    if parse_results == False:
                        # We check == False, and don't use bool conversion, as an empty
                        # dict can be returned, if none of the available currencies is supported by the provider
                        _logger.warning('Unable to connect to the online exchange rate purchase platform %s. The web service may be temporary down.', currency_provider + '_purchase')
                        rslt = False
                    else:
                        for result in parse_results:
                            companies._generate_purchase_currency_rates(result)

        return rslt

    def _parse_bcrp_update_purchase_data(self, available_currencies):
        """Bank of Peru (bcrp)
        API Doc: https://estadisticas.bcrp.gob.pe/estadisticas/series/ayuda/api
            - https://estadisticas.bcrp.gob.pe/estadisticas/series/api/[códigos de series]/[formato de salida]/[periodo inicial]/[periodo final]/[idioma]
        Source: https://estadisticas.bcrp.gob.pe/estadisticas/series/diarias/tipo-de-cambio
            PD04640PD	TC Sistema bancario SBS (S/ por US$) - Venta
            PD04648PD	TC Euro (S/ por Euro) - Venta
        """

        bcrp_date_format_url = '%Y-%m-%d'
        bcrp_date_format_res = '%d.%b.%y'
        result = {}
        available_currency_names = available_currencies.mapped('name')
        if 'PEN' not in available_currency_names:
            return result

        url_format = "https://estadisticas.bcrp.gob.pe/estadisticas/series/api/%(currency_code)s/json/%(date_start)s/%(date_end)s/ing"
        foreigns = {
            # currency code from webservices
            'USD': 'PD04639PD',
            'EUR': 'PD04647PD',
        }
        results = []
        dates = self.env['res.currency'].search([('name', 'in', list(foreigns.keys()))]).rate_ids.filtered(lambda r: r.purchase_rate == 1).mapped('name')
        for date_pe in dates:
            date_backup_pe = date_pe
            result = {}
            dates_null_rate = []
            for currency_odoo_code, currency_pe_code in foreigns.items():
                if currency_odoo_code not in available_currency_names:
                    continue
                second_pe_str = date_pe.strftime(bcrp_date_format_url)
                data = {
                    'date_start': second_pe_str,
                    'date_end': second_pe_str,
                }
                data.update({'currency_code': currency_pe_code})
                rate = 1
                while rate == 1:
                    try:
                        url = url_format % data
                        res = requests.get(url, timeout=10)
                        res.raise_for_status()
                        series = res.json()
                    except Exception as e:
                        _logger.error(e)
                        rate = 1
                        continue
                    else:
                        if series.get('periods', False):
                            print(url)
                            date_rate_str = series['periods'][-1]['name']
                            fetched_rate = float(series['periods'][-1]['values'][0])
                            rate = 1.0 / fetched_rate if fetched_rate else 0
                            if not rate:
                                continue
                            # This replace is done because the service is returning Set for September instead of Sep the value
                            # commonly accepted for September,
                            normalized_date = date_rate_str.replace('Set', 'Sep')
                            date_rate = datetime.datetime.strptime(normalized_date, bcrp_date_format_res).strftime(DEFAULT_SERVER_DATE_FORMAT)
                            result[currency_odoo_code] = (rate, date_rate)
                        else:
                            dates_null_rate.append(date_pe)
                            date_pe = date_pe - datetime.timedelta(days=1)
                            second_pe_str = date_pe.strftime(bcrp_date_format_url)
                            data = {
                                'date_start': second_pe_str,
                                'date_end': second_pe_str,
                            }
                            data.update({'currency_code': currency_pe_code})
                date_pe = date_backup_pe

            cop = result.copy()
            if cop:
                if dates_null_rate:
                    date = date_backup_pe
                    left_result = {}
                    for currency, rate in cop.items():
                        left_result[currency] = (rate[0], date.strftime(DEFAULT_SERVER_DATE_FORMAT))
                    left_result['PEN'] = (1.0, fields.Date.context_today(self.with_context(tz='America/Lima')))
                    left_cop = left_result.copy()
                    results.append(left_cop)
                else:
                    cop['PEN'] = (1.0, fields.Date.context_today(self.with_context(tz='America/Lima')))
                    results.append(cop)

        return results

    def update_currency_rates(self):
        ''' This method is used to update all currencies given by the provider.
        It calls the parse_function of the selected exchange rates provider automatically.

        For this, all those functions must be called _parse_xxx_data, where xxx
        is the technical name of the provider in the selection field. Each of them
        must also be such as:
            - It takes as its only parameter the recordset of the currencies
              we want to get the rates of
            - It returns a dictionary containing currency codes as keys, and
              the corresponding exchange rates as its values. These rates must all
              be based on the same currency, whatever it is. This dictionary must
              also include a rate for the base currencies of the companies we are
              updating rates from, otherwise this will result in an error
              asking the user to choose another provider.

        :return: True if the rates of all the records in self were updated
                 successfully, False if at least one wasn't.
        '''
        rslt = super(ResCompany, self).update_currency_rates()
        active_currencies = self.env['res.currency'].search([])
        if 'PEN' in active_currencies.mapped('name'):
            for (currency_provider, companies) in self._group_by_provider().items():
                parse_results = None
                if currency_provider == 'bcrp':
                    parse_function = getattr(companies, '_parse_' + currency_provider + '_purchase_data')
                    parse_results = parse_function(active_currencies)

                    if parse_results == False:
                        # We check == False, and don't use bool conversion, as an empty
                        # dict can be returned, if none of the available currencies is supported by the provider
                        _logger.warning('Unable to connect to the online exchange rate purchase platform %s. The web service may be temporary down.', currency_provider + '_purchase')
                        rslt = False
                    else:
                        companies._generate_purchase_currency_rates(parse_results)

        return rslt

    def _parse_bcrp_purchase_data(self, available_currencies):
        """Bank of Peru (bcrp)
        API Doc: https://estadisticas.bcrp.gob.pe/estadisticas/series/ayuda/api
            - https://estadisticas.bcrp.gob.pe/estadisticas/series/api/[códigos de series]/[formato de salida]/[periodo inicial]/[periodo final]/[idioma]
        Source: https://estadisticas.bcrp.gob.pe/estadisticas/series/diarias/tipo-de-cambio
            PD04640PD	TC Sistema bancario SBS (S/ por US$) - Venta
            PD04648PD	TC Euro (S/ por Euro) - Venta
        """

        bcrp_date_format_url = '%Y-%m-%d'
        bcrp_date_format_res = '%d.%b.%y'
        result = {}
        available_currency_names = available_currencies.mapped('name')
        if 'PEN' not in available_currency_names:
            return result
        url_format = "https://estadisticas.bcrp.gob.pe/estadisticas/series/api/%(currency_code)s/json/%(date_start)s/%(date_end)s/ing"
        foreigns = {
            # currency code from webservices
            'USD': 'PD04639PD',
            'EUR': 'PD04647PD',
        }
        date_pe = self.mapped('currency_next_execution_date')[0] or datetime.datetime.now(timezone('America/Lima'))
        results = []

        date_backup_pe = date_pe
        result = {}
        dates_null_rate = []
        for currency_odoo_code, currency_pe_code in foreigns.items():
            if currency_odoo_code not in available_currency_names:
                continue
            second_pe_str = date_pe.strftime(bcrp_date_format_url)
            data = {
                'date_start': second_pe_str,
                'date_end': second_pe_str,
            }
            data.update({'currency_code': currency_pe_code})
            rate = 1
            while rate == 1:
                try:
                    url = url_format % data
                    res = requests.get(url, timeout=10)
                    res.raise_for_status()
                    series = res.json()
                except Exception as e:
                    _logger.error(e)
                    rate = 1
                    continue
                else:
                    if series.get('periods', False):
                        print(url)
                        date_rate_str = series['periods'][-1]['name']
                        fetched_rate = float(series['periods'][-1]['values'][0])
                        rate = 1.0 / fetched_rate if fetched_rate else 0
                        if not rate:
                            continue
                        # This replace is done because the service is returning Set for September instead of Sep the value
                        # commonly accepted for September,
                        normalized_date = date_rate_str.replace('Set', 'Sep')
                        date_rate = datetime.datetime.strptime(normalized_date, bcrp_date_format_res).strftime(DEFAULT_SERVER_DATE_FORMAT)
                        result[currency_odoo_code] = (rate, date_rate)
                    # rate = 0
                    else:
                        dates_null_rate.append(date_pe)
                        date_pe = date_pe - datetime.timedelta(days=1)
                        second_pe_str = date_pe.strftime(bcrp_date_format_url)
                        data = {
                            'date_start': second_pe_str,
                            'date_end': second_pe_str,
                        }
                        data.update({'currency_code': currency_pe_code})
            date_pe = date_backup_pe
        cop = result.copy()
        if cop:
            if dates_null_rate:
                date = date_backup_pe
                left_result = {}
                for currency, rate in cop.items():
                    left_result[currency] = (rate[0], date.strftime(DEFAULT_SERVER_DATE_FORMAT))
                left_result['PEN'] = (1.0, datetime.date.today().strftime(DEFAULT_SERVER_DATE_FORMAT))
                left_cop = left_result.copy()
                results.append(left_cop)
            else:
                cop['PEN'] = (1.0, datetime.date.today().strftime(DEFAULT_SERVER_DATE_FORMAT))
                results.append(cop)
        return results and results[0] or {}

    def _generate_purchase_currency_rates(self, parsed_data):
        """ Generate the currency rate entries for each of the companies, using the
        result of a parsing function, given as parameter, to get the rates data.

        This function ensures the currency rates of each company are computed,
        based on parsed_data, so that the currency of this company receives rate=1.
        This is done so because a lot of users find it convenient to have the
        exchange rate of their main currency equal to one in Odoo.
        """
        Currency = self.env['res.currency']
        CurrencyRate = self.env['res.currency.rate']

        today = fields.Date.today()
        for company in self:
            rate_info = parsed_data.get(company.currency_id.name, None)

            if not rate_info:
                raise UserError(_("Your main currency (%s) is not supported by this exchange rate provider. Please choose another one.", company.currency_id.name))

            base_currency_rate = rate_info[0]

            for currency, (rate, date_rate) in parsed_data.items():
                rate_value = rate/base_currency_rate

                currency_object = Currency.search([('name', '=', currency)])
                already_existing_rate = CurrencyRate.search([('currency_id', '=', currency_object.id), ('name', '=', date_rate), ('company_id', '=', company.id)])
                if already_existing_rate:
                    already_existing_rate.purchase_rate = rate_value
                # ! comentado para evitar el error de que no exista ya que no tendría el tipo de cambio venta y eso generaría errores por las funciones pre existentes en el tipo de cambio venta.
                # else:
                #     CurrencyRate.create({'currency_id': currency_object.id, 'purchase_rate': rate_value, 'name': date_rate, 'company_id': company.id})

    def _parse_bcrp_data(self, available_currencies):
        return self._parse_bcrp_sale_data(available_currencies)

    def _parse_bcrp_sale_data(self, available_currencies):
        """Bank of Peru (bcrp)
        API Doc: https://estadisticas.bcrp.gob.pe/estadisticas/series/ayuda/api
            - https://estadisticas.bcrp.gob.pe/estadisticas/series/api/[códigos de series]/[formato de salida]/[periodo inicial]/[periodo final]/[idioma]
        Source: https://estadisticas.bcrp.gob.pe/estadisticas/series/diarias/tipo-de-cambio
            PD04640PD	TC Sistema bancario SBS (S/ por US$) - Venta
            PD04648PD	TC Euro (S/ por Euro) - Venta
        """

        bcrp_date_format_url = '%Y-%m-%d'
        bcrp_date_format_res = '%d.%b.%y'
        result = {}
        available_currency_names = available_currencies.mapped('name')
        if 'PEN' not in available_currency_names:
            return result
        url_format = "https://estadisticas.bcrp.gob.pe/estadisticas/series/api/%(currency_code)s/json/%(date_start)s/%(date_end)s/ing"
        foreigns = {
            # currency code from webservices
            'USD': 'PD04640PD',
            'EUR': 'PD04648PD',
        }
        date_pe = self.mapped('currency_next_execution_date')[0] or datetime.datetime.now(timezone('America/Lima'))
        results = []

        date_backup_pe = date_pe
        result = {}
        dates_null_rate = []
        for currency_odoo_code, currency_pe_code in foreigns.items():
            if currency_odoo_code not in available_currency_names:
                continue
            second_pe_str = date_pe.strftime(bcrp_date_format_url)
            data = {
                'date_start': second_pe_str,
                'date_end': second_pe_str,
            }
            data.update({'currency_code': currency_pe_code})
            rate = 1
            while rate == 1:
                try:
                    url = url_format % data
                    res = requests.get(url, timeout=10)
                    res.raise_for_status()
                    series = res.json()
                except Exception as e:
                    _logger.error(e)
                    rate = 1
                    continue
                else:
                    if series.get('periods', False):

                        print(url)
                        date_rate_str = series['periods'][-1]['name']
                        fetched_rate = float(series['periods'][-1]['values'][0])
                        rate = 1.0 / fetched_rate if fetched_rate else 0
                        if not rate:
                            continue
                        # This replace is done because the service is returning Set for September instead of Sep the value
                        # commonly accepted for September,
                        normalized_date = date_rate_str.replace('Set', 'Sep')
                        date_rate = datetime.datetime.strptime(normalized_date, bcrp_date_format_res).strftime(DEFAULT_SERVER_DATE_FORMAT)
                        result[currency_odoo_code] = (rate, date_rate)
                    # rate = 0
                    else:
                        dates_null_rate.append(date_pe)
                        date_pe = date_pe - datetime.timedelta(days=1)
                        second_pe_str = date_pe.strftime(bcrp_date_format_url)
                        data = {
                            'date_start': second_pe_str,
                            'date_end': second_pe_str,
                        }
                        data.update({'currency_code': currency_pe_code})
            date_pe = date_backup_pe
        cop = result.copy()
        if cop:
            if dates_null_rate:
                date = date_backup_pe
                left_result = {}
                for currency, rate in cop.items():
                    left_result[currency] = (rate[0], date.strftime(DEFAULT_SERVER_DATE_FORMAT))
                left_result['PEN'] = (1.0, datetime.date.today().strftime(DEFAULT_SERVER_DATE_FORMAT))
                left_cop = left_result.copy()
                results.append(left_cop)
            else:
                cop['PEN'] = (1.0, datetime.date.today().strftime(DEFAULT_SERVER_DATE_FORMAT))
                results.append(cop)
        return results and results[0] or {}
