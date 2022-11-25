from odoo import _, api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'
    _description = 'Account Move'

    sunat_table_25_id = fields.Many2one('sunat.table.25', string='Convenio para evitar doble Trib.')
    sunat_table_31_id = fields.Many2one('sunat.table.31', string='Tipo de renta')
    not_domiciled_purchase_move_period = fields.Selection([
        ('0', 'Anotación optativa sin efecto en el IGV corresponde al periodo.'),
        ('9', 'Ajuste o rectificación en la anotación de la información de una operación registrada en un periodo anterior.')
    ], string='Estado de factura de compra no domiciliado')
    not_domiciled = fields.Boolean('Es no domiciliado?', related='partner_id.not_domiciled')
