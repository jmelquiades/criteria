from odoo import _, api, fields, models


class L10NLatamTable10(models.Model):
    _name = 'l10n_latam.table.10'
    _description = 'L10N Latam Table 10'

    name = fields.Char('Name')
    code = fields.Char('Code')

    _sql_constraints = [
        ("name_unique", "unique(name)", "The name field must be unique."),
    ]
    _sql_constraints = [
        ("code_unique", "unique(code)", "The code field pair must be unique."),
    ]

    def name_get(self):
        result = []
        for record in self:
            name = f'({record.code}) {record.name}'
            result.append((record.id, name))
        return result
