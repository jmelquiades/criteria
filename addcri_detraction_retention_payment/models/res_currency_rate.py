from odoo import _, api, fields, models


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
