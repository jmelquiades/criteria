
from odoo import fields, models


class CodeCustoms(models.Model):

    _name = 'code.customs'

    name = fields.Char(
        string='Description',
        required=True
    )
    code = fields.Char(
        string='Code',
        required=True
    )
