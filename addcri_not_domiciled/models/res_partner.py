from odoo import _, api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'
    _description = 'Res Partner'

    not_domiciled = fields.Boolean('Es no domiciliado?')
