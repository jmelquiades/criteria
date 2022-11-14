from odoo import _, api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'
    _description = 'Res Company'

    detraction_inbound_account_id = fields.Many2one('account.account', string="Cuenta por pagar de detracciones", copy=True, groups="account.group_account_manager")
    detraction_outbound_account_id = fields.Many2one('account.account', string="Cuenta por cobrar de detracciones", copy=True, groups="account.group_account_manager")
