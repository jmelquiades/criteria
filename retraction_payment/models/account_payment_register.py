from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'
    _description = 'Account Payment Register'

    detraction_amount_residual = fields.Float('Detraction amount')
    no_detraction_amount_residual = fields.Float('Detraction amount')

    @api.constrains('journal_id', 'amount', 'detraction_amount_residual', 'no_detraction_amount_residual')
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

        payments = self.env['account.payment'].search([('partner_id', '=', move.partner_id.id)]).filtered(lambda r: move in r.reconciled_invoice_ids)
        payment_lines = self.env['account.move.line'].search([('partner_id', '=', move.partner_id.id), ('payment_id', 'in', payments.ids), ('reconciled', '=', True)])

        # * Calculo de límites

        detraction_amount_pay = abs(sum(payment_lines.filtered(lambda j: j.payment_id and j.journal_id.id == journal).mapped(lambda a: a.amount_currency)))  # * Viene con moneda del movimiento
        no_detraction_amount_pay = abs(sum(payment_lines.filtered(lambda j: j.payment_id and j.journal_id.id != journal).mapped(lambda a: a.amount_currency)))  # * Viene con moneda del movimiento

        # * Update data

        detraction_amount_residual = detraction_amount - detraction_amount_pay
        no_detraction_amount_residual = no_detraction_amount - no_detraction_amount_pay  # * data['source_amount'] data['source_currency_id'] están en moneda de la fuente

        data.update({
            'detraction_amount_residual': detraction_amount_residual,
            'no_detraction_amount_residual': no_detraction_amount_residual
        })
        return data
