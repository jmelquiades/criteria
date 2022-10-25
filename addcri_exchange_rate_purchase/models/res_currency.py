from odoo import _, api, fields, models


class ResCurrency(models.Model):
    _inherit = 'res.currency'
    _description = 'Res Currency'

    # * Purchase

    def _get_purchase_rates(self, company, date):
        if not self.ids:
            return {}
        self.env['res.currency.rate'].flush(['purchase_rate', 'currency_id', 'company_id', 'name'])
        query = """SELECT c.id,
                          COALESCE((SELECT r.purchase_rate FROM res_currency_rate r
                                  WHERE r.currency_id = c.id AND r.name <= %s
                                    AND (r.company_id IS NULL OR r.company_id = %s)
                               ORDER BY r.company_id, r.name DESC
                                  LIMIT 1), 1.0) AS rate
                   FROM res_currency c
                   WHERE c.id IN %s"""
        self._cr.execute(query, (date, company.id, tuple(self.ids)))
        currency_rates = dict(self._cr.fetchall())
        return currency_rates

    @api.model
    def _get_conversion_purchase_rate(self, from_currency, to_currency, company, date):
        currency_rates = (from_currency + to_currency)._get_purchase_rates(company, date)
        res = currency_rates.get(to_currency.id) / currency_rates.get(from_currency.id)
        return res

    def _convert_purchase(self, from_amount, to_currency, company, date, round=True, exchange_rate=0):
        """Returns the converted amount of ``from_amount``` from the currency
           ``self`` to the currency ``to_currency`` for the given ``date`` and
           company.

           :param company: The company from which we retrieve the convertion rate
           :param date: The nearest date from which we retriev the conversion rate.
           :param round: Round the result or not
        """
        self, to_currency = self or to_currency, to_currency or self
        assert self, "convert amount from unknown currency"
        assert to_currency, "convert amount to unknown currency"
        assert company, "convert amount from unknown company"
        assert date, "convert amount from unknown date"
        # apply conversion rate
        if self == to_currency:
            to_amount = from_amount
        else:
            manual_rate = dict(self._context).get('manual_rate', False)
            if manual_rate:
                if exchange_rate == 0:
                    raise
                to_amount = from_amount * exchange_rate
            else:
                to_amount = from_amount * self._get_conversion_purchase_rate(self, to_currency, company, date)
        # apply rounding
        return to_currency.round(to_amount) if round else to_amount

    # * Sale

    def _get_sale_rates(self, company, date):
        if not self.ids:
            return {}
        self.env['res.currency.rate'].flush(['sale_rate', 'currency_id', 'company_id', 'name'])
        query = """SELECT c.id,
                          COALESCE((SELECT r.sale_rate FROM res_currency_rate r
                                  WHERE r.currency_id = c.id AND r.name <= %s
                                    AND (r.company_id IS NULL OR r.company_id = %s)
                               ORDER BY r.company_id, r.name DESC
                                  LIMIT 1), 1.0) AS rate
                   FROM res_currency c
                   WHERE c.id IN %s"""
        self._cr.execute(query, (date, company.id, tuple(self.ids)))
        currency_rates = dict(self._cr.fetchall())
        return currency_rates

    @api.model
    def _get_conversion_sale_rate(self, from_currency, to_currency, company, date):
        currency_rates = (from_currency + to_currency)._get_sale_rates(company, date)
        res = currency_rates.get(to_currency.id) / currency_rates.get(from_currency.id)
        return res

    def _convert_sale(self, from_amount, to_currency, company, date, round=True, exchange_rate=0):
        """Returns the converted amount of ``from_amount``` from the currency
           ``self`` to the currency ``to_currency`` for the given ``date`` and
           company.

           :param company: The company from which we retrieve the convertion rate
           :param date: The nearest date from which we retriev the conversion rate.
           :param round: Round the result or not
        """
        self, to_currency = self or to_currency, to_currency or self
        assert self, "convert amount from unknown currency"
        assert to_currency, "convert amount to unknown currency"
        assert company, "convert amount from unknown company"
        assert date, "convert amount from unknown date"
        # apply conversion rate
        if self == to_currency:
            to_amount = from_amount
        else:
            manual_rate = dict(self._context).get('manual_rate', False)
            if manual_rate:
                if exchange_rate == 0:
                    raise
                to_amount = from_amount * exchange_rate
            else:
                to_amount = from_amount * self._get_conversion_sale_rate(self, to_currency, company, date)

        # apply rounding
        return to_currency.round(to_amount) if round else to_amount
