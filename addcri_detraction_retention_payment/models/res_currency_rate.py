from odoo import _, api, fields, models
from odoo.osv import expression


class ResCurrencyRate(models.Model):
    _inherit = 'res.currency.rate'
    _description = 'Res Currency rate'

    @api.model
    def create(self, vals):
        res = super(ResCurrencyRate, self).create(vals)
        if 'rate' in vals:
            self._execute_compute_exchange_rate_moves(vals)
        return res

    def write(self, vals):
        res = super(ResCurrencyRate, self).write(vals)
        if 'rate' in vals:
            self._execute_compute_exchange_rate_moves(vals)
        return res

    def _execute_compute_exchange_rate_moves(self, vals):
        AccountMove = self.env['account.move']
        company = vals.get('company_id', self.company_id)
        currency = vals.get('currency_id', self.currency_id)
        date = vals.get('name', self.name)

        domain = [('date', '>=', date), ('company_id', '=', company.id), ('currency_id', '=', currency.id)]

        next_dates = currency.rate_ids.filtered(lambda cr: cr.name > date).sorted(lambda d: d.name)
        next_date = next_dates[0].name if next_dates else False

        if next_date:
            domain_extra = [('date', '<', next_date)]
            domain = expression.AND([domain, domain_extra])
        moves = AccountMove.search(domain)
        moves._get_exchange_rate()
