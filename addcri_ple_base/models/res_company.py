from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    type_contributor = fields.Selection(selection=[
        ('CUO', 'Contribuyentes del Régimen General'),
        ('RER', 'Contribuyentes del Régimen Especial de Renta')
    ], string='Tipo de contribuyente', default='CUO')
