from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    detraction_inbound_account_id = fields.Many2one('account.account', related='company_id.detraction_inbound_account_id', string="Cuenta por pagar de detracciones", readonly=False)
    detraction_outbound_account_id = fields.Many2one('account.account', related='company_id.detraction_outbound_account_id', string="Cuenta por cobrar de detracciones", readonly=False)
