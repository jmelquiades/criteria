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
        result['PEN'] = (1.0, fields.Date.context_today(self.with_context(tz='America/Lima')))
        url_format = "https://estadisticas.bcrp.gob.pe/estadisticas/series/api/%(currency_code)s/json/%(date_start)s/%(date_end)s/ing"
        foreigns = {
            # currency code from webservices
            'USD': 'PD04639PD',
            'EUR': 'PD04647PD',
        }
        date_pe = self.mapped('currency_next_execution_date')[0] or datetime.datetime.now(timezone('America/Lima'))
        # In case the desired date does not have an exchange rate, it means that we must use the previous day until we
        # find a change. It is left 7 since in tests we have found cases of up to 5 days without update but no more
        # than that. That is not to say that that cannot change in the future, so we leave a little margin.
        first_pe_str = (date_pe - datetime.timedelta(days=7)).strftime(bcrp_date_format_url)
        second_pe_str = date_pe.strftime(bcrp_date_format_url)
        data = {
            'date_start': first_pe_str,
            'date_end': second_pe_str,
        }
        for currency_odoo_code, currency_pe_code in foreigns.items():
            if currency_odoo_code not in available_currency_names:
                continue
            data.update({'currency_code': currency_pe_code})
            url = url_format % data
            _logger.info(f'_parse_bcrp_purchase_data {url}')
            try:
                res = requests.get(url, timeout=10)
                res.raise_for_status()
                series = res.json()
            except Exception as e:
                _logger.error(e)
                continue
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
        return result

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
                _logger.info(f'_generate_purchase_currency_rates {currency_object} {date_rate} {company} {rate_value}')
                if already_existing_rate:
                    already_existing_rate.purchase_rate = rate_value
                else:
                    CurrencyRate.create({'currency_id': currency_object.id, 'purchase_rate': rate_value, 'name': date_rate, 'company_id': company.id})
