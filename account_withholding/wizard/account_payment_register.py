# -*- coding: utf-8 -*-
from collections import defaultdict
from lxml import etree

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, frozendict

import logging
log = logging.getLogger(__name__)


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    apply_withholding=fields.Boolean(string='Apply Withholding')
    withholdin_line_ids = fields.One2many('account.payment.register.withholding.line', 'payment_register_id')

    @api.model
    def default_get(self, fields_list):
        res = super(AccountPaymentRegister, self).default_get(fields_list)
        if self._context.get('active_model') == 'account.move':
            invoices = self.env['account.move'].browse(self._context.get('active_ids', []))
            res['withholdin_line_ids'] = [(0, 0, {
                'invoice_id':i.id
            }) for i in invoices]
        return res

class AccountPaymentRegisterWithholdingLine(models.TransientModel):
    _name = 'account.payment.register.withholding.line'

    payment_register_id = fields.Many2one('account.payment.register')
    invoice_id = fields.Many2one('account.move', string='Invoice', readonly=True)
    tax_ids = fields.Many2many('account.tax', string='Taxes')
    currency_id = fields.Many2one(related='invoice_id.currency_id')
    amount_balance = fields.Monetary(related='invoice_id.amount_residual')
    amount = fields.Monetary(string='Amount Tax', compute="_compute_amount")

    @api.depends('invoice_id','tax_ids')
    def _compute_amount(self):
        for rec in self:
            if rec.tax_ids and rec.invoice_id:
                tax_data = rec.tax_ids.compute_all(rec.amount_balance, rec.currency_id, 1)
                rec.amount = sum(t['amount'] for t in tax_data['taxes'])
            else:
                rec.amount = 0