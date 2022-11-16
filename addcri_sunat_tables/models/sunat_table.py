from odoo import _, api, fields, models


class SunatTable(models.AbstractModel):
    _name = 'sunat.table'
    _description = 'Sunat Table'

    name = fields.Char('Descripción')
    code = fields.Char('Código')

    _sql_constraints = [
        ("name_unique", "unique(name)", "El campo descripción debe de ser único."),
    ]
    _sql_constraints = [
        ("code_unique", "unique(code)", "El campo código debe de ser único."),
    ]
