from odoo import _, api, fields, models


class SunatTable31(models.Model):
    _name = 'sunat.table.31'
    _inherit = 'sunat.table'
    _description = 'Sunat Table 31'

    article = fields.Char('Artículo de la ley del impuesto a la renta y su reglamento')
    ocde_code = fields.Char('Código de renta según la OCDE')
