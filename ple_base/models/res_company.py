from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    type_contributor = fields.Selection(selection=[
        ('CUO', u'Contribuyentes del Régimen General'),
        ('RER', u'Contribuyentes del Régimen Especial de Renta')
    ], string='Tipo de contribuyente')

