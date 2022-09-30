# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    detraction_journal_id = fields.Many2one('account.journal', string='Detraction Journal', copy=True, groups="account.group_account_user")
