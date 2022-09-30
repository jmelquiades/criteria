from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'
    _description = 'Account Payment Register'

    detraction_amount_residual = fields.Float('Detraction amount')
    no_detraction_amount_residual = fields.Float('Detraction amount')

    @api.constrains('journal_id', 'amount')
    def _constrains_journal_id(self):
        detraction_amount_residual = self.source_currency_id._convert(self.detraction_amount_residual, self.currency_id, self.company_id, self.payment_date)
        no_detraction_amount_residual = self.source_currency_id._convert(self.no_detraction_amount_residual, self.currency_id, self.company_id, self.payment_date)
        journal = self.env.user.company_id.detraction_journal_id.id
        if self.journal_id.id == journal and self.amount > detraction_amount_residual:
            raise UserError('No puede pagar este monto en detracción.')
        elif self.journal_id.id != journal and self.amount > no_detraction_amount_residual:
            raise UserError('No puede pagar este monto en este diario (detracción)')

    def _get_wizard_values_from_batch(self, batch_result):
        data = super()._get_wizard_values_from_batch(batch_result)
        lines = batch_result['lines']
        move = lines.move_id
        is_detraction = self.env.context.get('is_detraction', False)
        journal = self.env.user.company_id.detraction_journal_id.id
        if is_detraction and not journal:
            raise UserError('Configurar el diario de detracciones.')
        detraction_amount = sum(lines.mapped('move_id.l10n_pe_dte_detraction_amount'))  # * Viene con moneda de la factura (fuente)
        no_detraction_amount = sum(lines.mapped('move_id.amount_total')) - detraction_amount  # * Viene con moneda de la factura (fuente)

        # * Búsqueda de pagos

        reconciled_amls = self._get_reconciled_move_lines(move)

        # payments = self.env['account.payment'].search([('partner_id', '=', move.partner_id.id)]).filtered(lambda r: move in r.reconciled_invoice_ids)
        # reconciled_amls = self.env['account.move.line'].search([('partner_id', '=', move.partner_id.id), ('payment_id', 'in', payments.ids), ('reconciled', '=', True)])

        # * Calculo de límites
        # ! j.payment_id and  se excluyé para tener en cuenta los otros mov. diferente de pagos (en prueba)
        detraction_amount_pay = abs(sum(reconciled_amls.filtered(lambda j: j.journal_id.id == journal).mapped(lambda a: a.amount_currency)))  # * Viene con moneda del movimiento
        no_detraction_amount_pay = abs(sum(reconciled_amls.filtered(lambda j: j.journal_id.id != journal).mapped(lambda a: a.amount_currency)))  # * Viene con moneda del movimiento

        # * Update data

        detraction_amount_residual = detraction_amount - detraction_amount_pay
        no_detraction_amount_residual = no_detraction_amount - no_detraction_amount_pay  # * data['source_amount'] data['source_currency_id'] están en moneda de la fuente

        data.update({
            'detraction_amount_residual': detraction_amount_residual,
            'no_detraction_amount_residual': no_detraction_amount_residual
        })
        return data

    def _get_reconciled_move_lines(self, move):
        """Helper used to retrieve the reconciled payments on this journal entry"""
        reconciled_lines = move.line_ids.filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
        reconciled_amls = reconciled_lines.mapped('matched_debit_ids.debit_move_id') + \
            reconciled_lines.mapped('matched_credit_ids.credit_move_id')
        return reconciled_amls
