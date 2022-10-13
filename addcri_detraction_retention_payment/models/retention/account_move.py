from odoo import _, api, fields, models
from odoo.exceptions import UserError

RETENTION_PAYMENT_STATE = [
    ('not_paid', 'No pagadas'),
    ('in_payment', 'En proceso de pago'),
    ('paid', 'Pagado'),
    ('partial', 'Pagado parcialmente'),
    ('unknown', 'No es retención'),
    # ('no_retention', 'No hay retención'),
]


class AccountMove(models.Model):
    _inherit = 'account.move'
    _description = 'Account Move'

    l10n_pe_dte_is_retention = fields.Boolean('Is retention?')
    retention_payment_state = fields.Selection(RETENTION_PAYMENT_STATE, string='Estado de pago de retención', compute='_get_retention_payment_state')

    def _get_retention_payment_state(self):
        for j in self:
            journal = self._get_retention_journal()
            if j.l10n_pe_dte_is_retention:
                retention_amount, retention_amount_pay = j._get_retention_amounts()
                if j.currency_id.is_zero(retention_amount_pay):
                    j.retention_payment_state = 'not_paid'
                elif retention_amount_pay < retention_amount:
                    j.retention_payment_state = 'partial'
                elif j.currency_id.is_zero(retention_amount_pay - retention_amount):
                    j.retention_payment_state = 'in_payment'
                    reconciled_payments = j._get_reconciled_payments().filtered(lambda j: j.journal_id == journal)
                    if not reconciled_payments or all(payment.is_matched for payment in reconciled_payments):
                        j.no_retention_payment_state = 'paid'
            else:
                j.retention_payment_state = 'unknown'

    def _get_retention_amounts(self, retention=True):
        retention_amount, no_retention_amount = self._get_retention_amount()
        retention_reconciciled_lines, no_retention_reconciciled_lines = self._get_retention_reconciled_move_lines(self._get_retention_journal())
        if retention:
            retention_amount_pay = abs(sum(retention_reconciciled_lines.mapped(lambda a: a.amount_currency)))  # * Viene con moneda del movimiento
            return retention_amount, retention_amount_pay
        no_retention_amount_pay = abs(sum(no_retention_reconciciled_lines.mapped(lambda a: a.amount_currency)))  # * Viene con moneda del movimiento
        return no_retention_amount, no_retention_amount_pay

    def _get_retention_amount(self):
        retention_amount = self.l10n_pe_dte_amount_retention_base  # * Viene con moneda de la factura (fuente)
        no_retention_amount = self.amount_total - retention_amount
        return retention_amount, no_retention_amount

    def _get_retention_journal(self):
        return self.env.user.company_id.retention_journal_id

    def _get_retention_reconciled_move_lines(self, journal=False):
        self.warning_retention_journal(journal)
        reconciled_amls = self._get_reconciled_move_lines()
        return self._get_info_aml_retention(reconciled_amls, journal)

    def _get_info_aml_retention(self, reconciled_amls, journal=False):
        self.warning_retention_journal(journal)
        retention_reconciciled_lines = reconciled_amls.filtered(lambda line: line.journal_id == journal)
        no_retention_reconciciled_lines = reconciled_amls - retention_reconciciled_lines
        return retention_reconciciled_lines, no_retention_reconciciled_lines

    def warning_retention_journal(self, journal):
        if not journal:
            raise UserError('Configurar el diario de retenciones.')

    def _get_reconciled_move_lines(self):
        """Helper used to retrieve the reconciled move line on this journal entry"""
        reconciled_lines = self.line_ids.filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
        reconciled_amls = reconciled_lines.mapped('matched_debit_ids.debit_move_id') + \
            reconciled_lines.mapped('matched_credit_ids.credit_move_id')
        return reconciled_amls
