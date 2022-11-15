from odoo import _, api, fields, models


class ResCountry(models.Model):
    _inherit = 'res.country'
    _description = 'Res Country'

    l10n_pe_country_code = fields.Char('Código SUNAT (35)')
