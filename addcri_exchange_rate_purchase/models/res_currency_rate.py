from odoo import _, api, fields, models


class ResCurrencyRate(models.Model):
    _inherit = 'res.currency.rate'
    _description = 'Res Currency Rate'

    purchase_rate = fields.Float('Purchase Rate')
