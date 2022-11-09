from odoo import _, api, fields, models


class MassivePaymentDetraction(models.Model):
    _name = 'massive.payment.detraction'
    _description = 'Massive Payment Detraction'

    name = fields.Char('name')
    txt_binary = fields.Binary('TXT')
    txt_filename = fields.Char()
    move_ids = fields.One2many('account.move', 'massive_payment_detraction_id', string='Pagos masivos')

    def get_account_moves_for_payment_detraccion(self):
        moves = self.env['account.move'].search([('l10n_pe_dte_is_detraction', '=', True), ('move_type', '=', 'in_invoice')]).filtered(lambda mv: mv.detraction_payment_state != 'paid')
        self.move_ids = [(6, 0, moves.ids)]
        self.get_massive_payment_txt()

    def get_massive_payment_txt(self):
        pass
