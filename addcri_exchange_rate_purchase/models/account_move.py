from odoo import _, api, fields, models
import logging


_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'
    _description = 'Account Move'

    exchange_rate = fields.Float('Tipo de cambio',  digits=(12, 3), store=True, compute='_get_exchange_rate', readonly=False)
    if_foreign_currency = fields.Boolean('Is foreign currency?', compute='_get_if_foreign_currency')

    @api.depends('currency_id', 'company_id.currency_id')
    def _get_if_foreign_currency(self):
        for record in self:
            record.if_foreign_currency = record.currency_id != record.company_id.currency_id

    @api.depends('date', 'currency_id', 'company_id', 'company_id.currency_id')
    def _get_exchange_rate(self):
        for record in self:
            record.exchange_rate = 1
            if record.move_type in record.get_inbound_types():
                record.exchange_rate = record.company_id.currency_id._get_conversion_purchase_rate(record.currency_id, record.company_id.currency_id, record.company_id, record.date)
            elif record.move_type in record.get_outbound_types():
                record.exchange_rate = record.company_id.currency_id._get_conversion_sale_rate(record.currency_id, record.company_id.currency_id, record.company_id, record.date)

    @api.onchange('exchange_rate')
    def _onchange_price_subtotal_from_exchange_rate(self):
        lines = (self.line_ids | self.invoice_line_ids)
        lines._onchange_price_subtotal()


    def _recompute_dynamic_lines(self, recompute_all_taxes=False, recompute_tax_base_amount=False):
        super(AccountMove, self)._recompute_dynamic_lines(recompute_all_taxes, recompute_tax_base_amount)
        self._onchange_price_subtotal_from_exchange_rate()

