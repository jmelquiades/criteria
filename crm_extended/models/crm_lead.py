from odoo import fields, models

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    needed_quality = fields.Char()