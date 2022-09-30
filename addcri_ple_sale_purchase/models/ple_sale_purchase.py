from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PlePurchaseSale(models.Model):
    _name = 'ple.sale.purchase'
    _inherit = 'ple.base'
    _description = 'Ple Purchase Sale'

    @api.depends('ple_sale_id', 'ple_purchase_id')
    def _get_status_ples(self):
        for record in self:
            record.ple_sale_state = record.ple_sale_id.state
            record.ple_purchase_state = record.ple_purchase_id.state

    ple_sale_id = fields.Many2one('ple.sale', string='Ple Ventas')
    ple_purchase_id = fields.Many2one('ple.purchase', string='Ple Compras')
    ple_sale_state = fields.Selection(selection=[
        ('draft', 'No declarado'),
        ('closed', 'Declarado')
    ], string='Estado PLE Ventas', compute=_get_status_ples)
    ple_purchase_state = fields.Selection(selection=[
        ('draft', 'No declarado'),
        ('closed', 'Declarado')
    ], string='Estado PLE Compras', compute=_get_status_ples)

    # def default_get(self, fields_list):
    #     res = super(PlePurchaseSale, self).default_get(fields_list)
    #     res.update({
    #         'state': 'closed'
    #     })
    #     return res

    def unlink(self):
        for record in self:
            if record.ple_sale_id or record.ple_purchase_id:
                raise UserError('No se puede eliminar ya que existen PLE\'s de este período')
        return super(PlePurchaseSale, self).unlink()
