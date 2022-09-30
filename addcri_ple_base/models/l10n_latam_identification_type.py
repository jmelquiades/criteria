from odoo import _, api, fields, models


class L10nLatamIdentificationType(models.Model):

    _inherit = 'l10n_latam.identification.type'

    code = fields.Char(
        string='Código',
        required=True
    )

    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'El código ya fue utilizado.'),

    ]
