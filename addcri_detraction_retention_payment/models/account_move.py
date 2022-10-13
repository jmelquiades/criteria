from odoo import _, api, fields, models


BASE_PAYMENT_STATE = [
    ('not_paid', 'No pagadas'),
    ('in_payment', 'En proceso de pago'),
    ('paid', 'Pagado'),
    ('partial', 'Pagado parcialmente'),
    ('unknown', 'Desconocido'),
    ('no_detraction', 'No hay detracción'),
]


class AccountMove(models.Model):
    _inherit = 'account.move'
    _description = 'Account Move'

    base_payment_state = fields.Selection(BASE_PAYMENT_STATE, string='Estado de pago de no detracción', compute='_get_base_payment_state')

    # @api.depends('line_ids.matched_debit_ids.debit_move_id', 'line_ids.matched_credit_ids.credit_move_id')
    def _get_base_payment_state(self):
        for j in self:
            # detraction_reconciciled_lines, no_detraction_reconciciled_lines = j._get_detraction_reconciled_move_lines(self._get_detraction_journal())
            # detraction_amount_pay = abs(sum(detraction_reconciciled_lines.mapped(lambda a: a.amount_currency)))  # * Viene con moneda del movimiento
            # no_detraction_amount_pay = abs(sum(no_detraction_reconciciled_lines.mapped(lambda a: a.amount_currency)))  # * Viene con moneda del movimiento
            # detraction_amount, no_detraction_amount = j._get_detraction_amount()
            journal = self._get_detraction_journal()
            no_detraction_amount, no_detraction_amount_pay = j._get_detraction_amounts(False)
            if not j.l10n_pe_dte_is_detraction:
                j.base_payment_state = 'no_detraction'
            elif j.currency_id.is_zero(no_detraction_amount_pay):
                j.base_payment_state = 'not_paid'
            elif no_detraction_amount_pay < no_detraction_amount:
                j.base_payment_state = 'partial'
            elif j.currency_id.is_zero(no_detraction_amount_pay - no_detraction_amount):
                j.base_payment_state = 'in_payment'
                reconciled_payments = j._get_reconciled_payments().filtered(lambda j: j.journal_id == journal)
                if not reconciled_payments or all(payment.is_matched for payment in reconciled_payments):
                    j.base_payment_state = 'paid'
            else:
                j.base_payment_state = 'unknown'
