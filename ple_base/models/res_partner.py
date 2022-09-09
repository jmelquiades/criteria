from odoo import _, api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'
    _description = 'Res Partner'

    is_nodomicilied = fields.Boolean('Is Nodomicilied')
