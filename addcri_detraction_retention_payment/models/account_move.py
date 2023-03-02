from odoo import _, api, fields, models
from odoo.exceptions import UserError
import logging


_logger = logging.getLogger(__name__)


BASE_PAYMENT_STATE = [
    ('not_paid', 'No pagadas'),
    ('in_payment', 'En proceso de pago'),
    ('paid', 'Pagado'),
    ('partial', 'Pagado parcialmente'),
    ('unknown', 'No aplica'),
    # ('no_detraction', 'No hay detracción'),
]


class AccountMove(models.Model):
    _inherit = 'account.move'
    _description = 'Account Move'

    # base_payment_state = fields.Selection(BASE_PAYMENT_STATE, string='Estado de pago de no detracción', compute='_get_base_payment_state')

    @api.constrains('l10n_pe_dte_is_retention', 'l10n_pe_dte_is_detraction')
    def _constrains_l10n_pe_dte_is_retention(self):
        if self.l10n_pe_dte_is_detraction and self.l10n_pe_dte_is_retention:
            raise UserError('La factura no puede ser detracción y retención a la vez.')

    # def _get_base_payment_state(self):
    #     for j in self:
    #         journal = self._get_detraction_journal()
    #         if j.l10n_pe_dte_is_detraction and j.move_type in ('out_invoice', 'in_invoice'):
    #             no_detraction_amount, no_detraction_amount_pay = j._get_detraction_amounts(False)
    #             if j.currency_id.is_zero(no_detraction_amount_pay):
    #                 j.base_payment_state = 'not_paid'
    #             elif no_detraction_amount_pay < no_detraction_amount:
    #                 j.base_payment_state = 'partial'
    #             elif j.currency_id.is_zero(no_detraction_amount_pay - no_detraction_amount):
    #                 j.base_payment_state = 'in_payment'
    #                 if j.move_type == 'out_invoice':
    #                     reconciled_payments = j._get_reconciled_payments().filtered(lambda j: j.journal_id != journal)
    #                 elif j.move_type == 'in_invoice':
    #                     reconciled_payments = j._get_reconciled_payments().filtered(lambda j: j.payment_id.payment_method_line_id.name != 'Detracciones')
    #                 if not reconciled_payments or all(payment.is_matched for payment in reconciled_payments):
    #                     j.base_payment_state = 'paid'
    #                 # else:
    #                 #     j.base_payment_state = 'unknown'
    #             else:
    #                 j.base_payment_state = 'unknown'
    #         elif j.l10n_pe_dte_is_retention:
    #             no_retention_amount, no_retention_amount_pay = j._get_retention_amounts(False)
    #             if j.currency_id.is_zero(no_retention_amount_pay):
    #                 j.base_payment_state = 'not_paid'
    #             elif no_retention_amount_pay < no_retention_amount:
    #                 j.base_payment_state = 'partial'
    #             elif j.currency_id.is_zero(no_retention_amount_pay - no_retention_amount):
    #                 j.base_payment_state = 'in_payment'
    #                 reconciled_payments = j._get_reconciled_payments().filtered(lambda j: j.journal_id == journal)
    #                 if not reconciled_payments or all(payment.is_matched for payment in reconciled_payments):
    #                     j.base_payment_state = 'paid'
    #         else:
    #             j.base_payment_state = 'unknown'
