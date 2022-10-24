from odoo import _, api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'
    _description = 'Account Move'

    exchange_rate = fields.Float('Tipo de cambio',  digits=(12, 3), store=True, compute='_get_exchange_rate', readonly=False)
    if_foreign_currency = fields.Boolean('Foreign Currency', compute='_get_if_foreign_currency')

    @api.depends('currency_id', 'company_id.currency_id')
    def _get_if_foreign_currency(self):
        for record in self:
            record.if_foreign_currency = record.currency_id != record.company_id.currency_id

    @api.depends('date', 'currency_id', 'company_id', 'company_id.currency_id')
    def _get_exchange_rate(self):
        self.exchange_rate = 0
        if self.move_type == 'out_invoice':
            self.exchange_rate = self.company_id.currency_id._get_conversion_purchase_rate(self.currency_id, self.company_id.currency_id, self.company_id, self.date)
        elif self.move_type == 'in_invoice':
            self.exchange_rate = self.company_id.currency_id._get_conversion_sale_rate(self.currency_id, self.company_id.currency_id, self.company_id, self.date)
