from odoo import _, api, fields, models
import math
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'
    _description = 'Account Move'

    @api.depends('l10n_pe_dte_operation_type')
    def _get_is_detraction(self):
        for record in self:
            if record.l10n_pe_dte_operation_type in ['1001', '1002', '1003', '1004']:
                record.l10n_pe_dte_is_detraction = True

    l10n_pe_dte_is_detraction = fields.Boolean(compute=_get_is_detraction, store=True)

    @api.constrains('l10n_pe_dte_detraction_code', 'l10n_pe_dte_is_detraction')
    def _constrains_l10n_pe_dte_detraction_percent(self):
        if self.l10n_pe_dte_is_detraction and not self.l10n_pe_dte_detraction_code:
            raise UserError('Definir el tipo de detracción')

    @api.constrains('l10n_pe_dte_operation_type', 'l10n_pe_dte_detraction_base')
    def _constrains_l10n_pe_dte_operation_type_l10n_pe_dte_detraction_base(self):
        if self.l10n_pe_dte_operation_type in ['1001', '1002', '1003', '1004'] and self.l10n_pe_dte_detraction_base <= 700:  # ! Esos 700 debe ser parte de cnfiguración.
            raise UserError('Esta operación no puede estar sujeta a detracción ya que el monto total no excede el monto mínimo.')

    @api.onchange('invoice_line_ids', 'l10n_pe_dte_detraction_percent')  # ! esto debería de ser computado
    def _onchange_detraction_percent(self):
        self._recompute_tax_lines()
        super(AccountMove, self)._onchange_detraction_percent()
        if self.l10n_pe_dte_is_detraction:
            self.l10n_pe_dte_detraction_amount = math.ceil(self.l10n_pe_dte_detraction_amount)
        else:
            self.l10n_pe_dte_detraction_amount = 0  # Todo: hacer readonly en la vista estos campos!
            self.l10n_pe_dte_detraction_base = 0

    def action_register_payment(self):
        action = super().action_register_payment()
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
            journal = self.env.user.company_id.detraction_journal_id.id
            lines = lines.filtered(lambda line: line.move_id.id != move.id)
            detraction_no_reconciciled_lines = lines.filtered(lambda line: line.journal_id.id == journal)
            no_detraction_no_reconciciled_lines = lines - detraction_no_reconciciled_lines

            # * Búsqueda de pagos
            reconciled_amls = self._get_reconciled_move_lines()

            detraction_reconciciled_lines = reconciled_amls.filtered(lambda line: line.journal_id.id == journal)
            no_detraction_reconciciled_lines = reconciled_amls - detraction_reconciciled_lines

            detraction_lines = detraction_no_reconciciled_lines | detraction_reconciciled_lines
            no_detraction_lines = no_detraction_no_reconciciled_lines | no_detraction_reconciciled_lines

            # * Calculo de límites
            # ! j.payment_id and en ambs filtered de abajo retirado
            detraction_amount_pay = abs(sum(detraction_lines.mapped(lambda a: a.amount_currency)))  # * Viene con moneda del movimiento
            no_detraction_amount_pay = abs(sum(no_detraction_lines.mapped(lambda a: a.amount_currency)))  # * Viene con moneda del movimiento
            detraction_amount = self.l10n_pe_dte_detraction_amount  # * Viene con moneda de la factura (fuente)
            no_detraction_amount = self.amount_total - detraction_amount  # * Viene con moneda de la factura (fuente)

            if detraction_amount < detraction_amount_pay or no_detraction_amount < no_detraction_amount_pay:
                raise UserError('No tiene permitido conciliar estos montos, verifique el monto de pago destinado a detracción.')
            return super().js_assign_outstanding_line(line_id)

    def _get_reconciled_move_lines(self):
        """Helper used to retrieve the reconciled move line on this journal entry"""
        reconciled_lines = self.line_ids.filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
        reconciled_amls = reconciled_lines.mapped('matched_debit_ids.debit_move_id') + \
            reconciled_lines.mapped('matched_credit_ids.credit_move_id')
        return reconciled_amls
