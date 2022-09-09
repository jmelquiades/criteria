from odoo import fields, models


class AccountRetention(models.Model):

    _name = 'account.retention'

    name = fields.Char(
        string='Name',
        required=True
    )
