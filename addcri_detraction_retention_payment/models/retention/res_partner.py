 from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'
    _description = 'Res Partner'

    is_retention = fields.Boolean('Is retention', default=False)
    retention_percentage = fields.Selection([
        ('3', '3%'),
        ('6', '6%')
    ], string='Retention Percentage')

    @api.constrains('is_retention', 'retention_percentage')
    def _constrains_is_retention_retention_percentage(self):
        if self.is_retention and not self.retention_percentage:
            raise UserError(_('You must select the retention percentage.'))
