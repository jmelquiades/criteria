from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'
    _description = 'Account Payment Register'

    retention_amount_residual = fields.Float('Detraction amount')
    no_retention_amount_residual = fields.Float('Detraction amount')
    is_retention = fields.Boolean('Is Detraction')

    @api.constrains('journal_id', 'amount', 'is_retention')
    def _constrains_journal_amount_retention(self):
        journal = self.env.user.company_id.retention_journal_id
        if self.is_retention:
            if not journal:
                raise UserError('Configurar el diario de pagos de detracción.')

            retention_amount_residual = self.source_currency_id._convert(self.retention_amount_residual, self.currency_id, self.company_id, self.payment_date)
            no_retention_amount_residual = self.source_currency_id._convert(self.no_retention_amount_residual, self.currency_id, self.company_id, self.payment_date)

            if self.journal_id == journal and self.amount > retention_amount_residual:
                raise UserError('No puede pagar este monto en detracción.')
            elif self.journal_id != journal and self.amount > no_retention_amount_residual:
                raise UserError('No puede pagar este monto en este diario (detracción)')

    def _get_wizard_values_from_batch(self, batch_result):
        data = super()._get_wizard_values_from_batch(batch_result)
        lines = batch_result['lines']
        move = lines.move_id
        is_retention = self.env.context.get('is_retention', False)
        journal = self.env.user.company_id.retention_journal_id
        if is_retention and not journal:
            raise UserError('Configurar el diario de detracciones.')
        retention_amount = sum(lines.mapped('move_id.l10n_pe_dte_amount_retention_base'))  # * Viene con moneda de la factura (fuente)
        no_retention_amount = sum(lines.mapped('move_id.amount_total')) - retention_amount  # * Viene con moneda de la factura (fuente)

        # * Búsqueda de pagos

        reconciled_amls = self._get_reconciled_move_lines(move)

        # * Calculo de límites
        # ! j.payment_id and  se excluyé para tener en cuenta los otros mov. diferente de pagos (en prueba)
        retention_amount_pay = abs(sum(reconciled_amls.filtered(lambda j: j.journal_id == journal).mapped(lambda a: a.amount_currency)))  # * Viene con moneda del movimiento
        no_retention_amount_pay = abs(sum(reconciled_amls.filtered(lambda j: j.journal_id != journal).mapped(lambda a: a.amount_currency)))  # * Viene con moneda del movimiento

        # * Update data

        retention_amount_residual = retention_amount - retention_amount_pay
        no_retention_amount_residual = no_retention_amount - no_retention_amount_pay  # * data['source_amount'] data['source_currency_id'] están en moneda de la fuente

        data.update({
            'retention_amount_residual': retention_amount_residual,
            'no_retention_amount_residual': no_retention_amount_residual,
            'is_retention': is_retention
        })
        return data
