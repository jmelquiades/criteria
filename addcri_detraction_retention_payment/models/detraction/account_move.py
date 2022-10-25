from odoo import _, api, fields, models
import math
from odoo.exceptions import UserError

DETRACTION_PAYMENT_STATE = [
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

    @api.depends('l10n_pe_dte_operation_type')
    def _get_is_detraction(self):
        for record in self:
            if record.l10n_pe_dte_operation_type in ['1001', '1002', '1003', '1004']:
                record.l10n_pe_dte_is_detraction = True
            else:
                record.l10n_pe_dte_is_detraction = False

    l10n_pe_dte_is_detraction = fields.Boolean(compute=_get_is_detraction, store=True)
    detraction_payment_state = fields.Selection(DETRACTION_PAYMENT_STATE, string='Estado de pago de detracción', compute='_get_detraction_payment_state')

    @api.onchange('l10n_pe_dte_operation_type')
    def _onchange_l10n_pe_dte_operation_type_detraction(self):
        if self.l10n_pe_dte_operation_type not in ['1001', '1002', '1003', '1004']:
            self.l10n_pe_dte_detraction_code = False
            self.l10n_pe_dte_detraction_percent = False

    # @api.depends('line_ids.matched_debit_ids.debit_move_id', 'line_ids.matched_credit_ids.credit_move_id')
    def _get_detraction_payment_state(self):
        for j in self:
            journal = self._get_detraction_journal()
            if j.l10n_pe_dte_is_detraction:
                detraction_amount, detraction_amount_pay = j._get_detraction_amounts()
                if j.currency_id.is_zero(detraction_amount_pay):
                    j.detraction_payment_state = 'not_paid'
                elif detraction_amount_pay < detraction_amount:
                    j.detraction_payment_state = 'partial'
                elif j.currency_id.is_zero(detraction_amount_pay - detraction_amount):
                    j.detraction_payment_state = 'in_payment'
                    reconciled_payments = j._get_reconciled_payments().filtered(lambda j: j.journal_id == journal)
                    if not reconciled_payments or all(payment.is_matched for payment in reconciled_payments):
                        j.detraction_payment_state = 'paid'
            else:
                j.detraction_payment_state = 'unknown'

    def _get_detraction_amounts(self, detraction=True):
        detraction_amount, no_detraction_amount = self._get_detraction_amount()
        detraction_reconciciled_lines, no_detraction_reconciciled_lines = self._get_detraction_reconciled_move_lines(self._get_detraction_journal())
        if detraction:
            detraction_amount_pay = abs(sum(detraction_reconciciled_lines.mapped(lambda a: a.amount_currency)))  # * Viene con moneda del movimiento
            return detraction_amount, detraction_amount_pay
        no_detraction_amount_pay = abs(sum(no_detraction_reconciciled_lines.mapped(lambda a: a.amount_currency)))  # * Viene con moneda del movimiento
        return no_detraction_amount, no_detraction_amount_pay

    @api.constrains('l10n_pe_dte_detraction_code', 'l10n_pe_dte_is_detraction')
    def _constrains_l10n_pe_dte_detraction_percent(self):
        if self.l10n_pe_dte_is_detraction and not self.l10n_pe_dte_detraction_code:
            raise UserError('Definir el tipo de detracción')

    @api.constrains('l10n_pe_dte_operation_type', 'l10n_pe_dte_detraction_base')
    def _constrains_l10n_pe_dte_operation_type_l10n_pe_dte_detraction_base(self):
        if self.l10n_pe_dte_operation_type in ['1001', '1002', '1003', '1004'] and self.l10n_pe_dte_detraction_base <= 700:  # ! Esos 700 debe ser parte de cnfiguración.
            raise UserError('Esta operación no puede estar sujeta a detracción ya que el monto total no excede el monto mínimo.')

    @api.onchange('invoice_line_ids', 'l10n_pe_dte_operation_type', 'l10n_pe_dte_detraction_percent', 'date', 'exchange_rate')  # ! esto debería de ser computado
    def _onchange_detraction_percent(self):
        self._compute_amount()
        self._compute_tax_totals_json()
        super(AccountMove, self)._onchange_detraction_percent()
        if self.l10n_pe_dte_is_detraction:
            self.l10n_pe_dte_detraction_amount = round(self.l10n_pe_dte_detraction_amount, 0)
        else:
            self.l10n_pe_dte_detraction_amount = 0
            self.l10n_pe_dte_detraction_base = 0

    def action_register_payment(self):
        action = super().action_register_payment()
        if self.l10n_pe_dte_is_detraction:
            action['context'].update(is_detraction=True)
        return action

    def js_assign_outstanding_line(self, line_id):
        ''' Called by the 'payment' widget to reconcile a suggested journal item to the present
        invoice.

        :param line_id: The id of the line to reconcile with the current invoice.
        '''
        self.ensure_one()
        lines = self.env['account.move.line'].browse(line_id)
        lines += self.line_ids.filtered(lambda line: line.account_id == lines[0].account_id and not line.reconciled)
        move = self
        if not self.l10n_pe_dte_is_detraction:
            return super().js_assign_outstanding_line(line_id)
        else:
            journal = self._get_detraction_journal()
            lines = lines.filtered(lambda line: line.move_id != move)
            detraction_no_reconciciled_lines = lines.filtered(lambda line: line.journal_id == journal)
            no_detraction_no_reconciciled_lines = lines - detraction_no_reconciciled_lines

            # * Búsqueda de pagos
            detraction_reconciciled_lines, no_detraction_reconciciled_lines = self._get_detraction_reconciled_move_lines(journal)

            detraction_lines = detraction_no_reconciciled_lines | detraction_reconciciled_lines
            no_detraction_lines = no_detraction_no_reconciciled_lines | no_detraction_reconciciled_lines

            # * Calculo de límites
            # ! j.payment_id and en ambs filtered de abajo retirado
            detraction_amount_pay = abs(sum(detraction_lines.mapped(lambda a: a.amount_currency)))  # * Viene con moneda del movimiento
            no_detraction_amount_pay = abs(sum(no_detraction_lines.mapped(lambda a: a.amount_currency)))  # * Viene con moneda del movimiento
            # detraction_amount = self.l10n_pe_dte_detraction_amount  # * Viene con moneda de la factura (fuente)
            # no_detraction_amount = self.amount_total - detraction_amount  # * Viene con moneda de la factura (fuente)
            detraction_amount, no_detraction_amount = self._get_detraction_amount()

            if detraction_amount < detraction_amount_pay or no_detraction_amount < no_detraction_amount_pay:
                raise UserError('No tiene permitido conciliar estos montos, verifique el monto de pago destinado a detracción.')
            return super().js_assign_outstanding_line(line_id)

    def _get_reconciled_move_lines(self):
        """Helper used to retrieve the reconciled move line on this journal entry"""
        reconciled_lines = self.line_ids.filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
        reconciled_amls = reconciled_lines.mapped('matched_debit_ids.debit_move_id') + \
            reconciled_lines.mapped('matched_credit_ids.credit_move_id')
        return reconciled_amls

    def _get_info_aml_detraction(self, reconciled_amls, journal=False):
        self.warning_detraction_journal(journal)
        detraction_reconciciled_lines = reconciled_amls.filtered(lambda line: line.journal_id == journal)
        no_detraction_reconciciled_lines = reconciled_amls - detraction_reconciciled_lines
        return detraction_reconciciled_lines, no_detraction_reconciciled_lines

    def _get_detraction_reconciled_move_lines(self, journal=False):
        self.warning_detraction_journal(journal)
        reconciled_amls = self._get_reconciled_move_lines()
        return self._get_info_aml_detraction(reconciled_amls, journal)

    def warning_detraction_journal(self, journal):
        if not journal:
            raise UserError('Configurar el diario de detracciones.')

    def _get_detraction_amount(self):
        detraction_amount = self.l10n_pe_dte_detraction_amount  # * Viene con moneda de la factura (fuente)
        no_detraction_amount = self.amount_total - detraction_amount
        return detraction_amount, no_detraction_amount

    def _get_detraction_journal(self):
        return self.env.user.company_id.detraction_journal_id
