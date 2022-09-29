# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    detraction_journal_id = fields.Many2one('account.journal', related='company_id.detraction_journal_id', string="Detraction Journal", readonly=False)
