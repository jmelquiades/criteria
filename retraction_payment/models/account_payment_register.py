from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'
    _description = 'Account Payment Register'

    @api.constrains('journal_id', 'amount')
    def _constrains_journal_id(self):
        if self.journal_id.detraction_journal and self.amount >= 83:  # ! monto restante de pago en detraccion y no detraccion cuando se trata de una detraccion
            raise UserError('No puede pagar este monto en detracción.')
        elif not self.journal_id.detraction_journal and self.amount >= 826 - 83:  # ! monto restante de pago en detraccion y no detraccion cuando se trata de una detraccion
            raise UserError('No puede pagar este monto en este diario (detracción)')
