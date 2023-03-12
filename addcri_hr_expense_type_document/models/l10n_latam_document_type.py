# -*- coding: utf-8 -*-
# from odoo import models, fields, api
from odoo import models, fields,api

class L10nLatamDocumentType(models.Model):
    
    _inherit= 'l10n_latam.document.type'

    use_in_expense = fields.Boolean(
        string='Use in Expenses',
        help='Active para que se vea en Gastos'
    )

