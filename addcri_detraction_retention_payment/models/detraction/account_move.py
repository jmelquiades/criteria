from odoo import _, api, fields, models, tools
import math
from odoo.exceptions import UserError, ValidationError

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
    # detraction_payment_state = fields.Selection(DETRACTION_PAYMENT_STATE, string='Estado de pago de detracción', compute='_get_detraction_payment_state')

    @api.onchange('l10n_pe_dte_operation_type')
    def _onchange_l10n_pe_dte_operation_type_detraction(self):
        if self.l10n_pe_dte_operation_type not in ['1001', '1002', '1003', '1004']:
            self.l10n_pe_dte_detraction_code = False
            self.l10n_pe_dte_detraction_percent = False
            self.onchange_detraction_percent()

    # def _get_detraction_payment_state(self):
    #     for j in self:
    #         journal = self._get_detraction_journal()
    #         if j.l10n_pe_dte_is_detraction and j.move_type in ('out_invoice', 'in_invoice'):
    #             detraction_amount, detraction_amount_pay = j._get_detraction_amounts()
    #             if j.currency_id.is_zero(detraction_amount_pay):
    #                 j.detraction_payment_state = 'not_paid'
    #             elif detraction_amount_pay < detraction_amount:
    #                 j.detraction_payment_state = 'partial'
    #             elif j.currency_id.is_zero(detraction_amount_pay - detraction_amount):
    #                 j.detraction_payment_state = 'in_payment'
    #                 if j.move_type == 'out_invoice':
    #                     reconciled_payments = j._get_reconciled_payments().filtered(lambda j: j.journal_id == journal)
    #                 elif j.move_type == 'in_invoice':
    #                     reconciled_payments = j._get_reconciled_payments().filtered(lambda j: j.payment_id.payment_method_line_id.name == 'Detracciones')
    #                 if not reconciled_payments or all(payment.is_matched for payment in reconciled_payments):
    #                     j.detraction_payment_state = 'paid'
    #                 # else:
    #                 #     j.detraction_payment_state = 'unknown'
    #             else:
    #                 j.detraction_payment_state = 'unknown'
    #         else:
    #             j.detraction_payment_state = 'unknown'

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
            raise ValidationError('Definir el tipo de detracción')

    def validate_l10n_pe_dte_detraction_base(self, vals):
        if ('l10n_pe_dte_detraction_base' in vals or 'l10n_pe_dte_detraction_amount' in vals) and len(set(vals.keys()).difference(set(['l10n_pe_dte_detraction_base', 'l10n_pe_dte_detraction_amount']))):
            l10n_pe_dte_detraction_base = vals.get('l10n_pe_dte_detraction_base', self.l10n_pe_dte_detraction_base) or self.l10n_pe_dte_detraction_base
            l10n_pe_dte_operation_type = vals.get('l10n_pe_dte_operation_type', self.l10n_pe_dte_operation_type)
            if l10n_pe_dte_operation_type in ['1001', '1002', '1003', '1004'] and l10n_pe_dte_detraction_base <= 700:  # ! Esos 700 debe ser parte de cnfiguración.
                raise ValidationError('Esta operación no puede estar sujeta a detracción ya que el monto total no excede el monto mínimo.')

    @api.model
    def create(self, vals):
        self.validate_l10n_pe_dte_detraction_base(vals)
        return super(AccountMove, self).create(vals)

    def write(self, vals):
        self.validate_l10n_pe_dte_detraction_base(vals)
        return super(AccountMove, self).write(vals)

    @api.constrains('l10n_pe_dte_operation_type')
    def _constrains_l10n_pe_dte_operation_type_l10n_pe_dte_detraction_base(self):
        self.onchange_detraction_percent()
        if self.l10n_pe_dte_operation_type in ['1001', '1002', '1003', '1004'] and self.l10n_pe_dte_detraction_base <= 700:  # ! Esos 700 debe ser parte de cnfiguración.
            raise ValidationError('Esta operación no puede estar sujeta a detracción ya que el monto total no excede el monto mínimo.')

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
        
        lines = self.get_account_move_line(line_id)
        lines += self.line_ids.filtered(lambda line: line.account_id == lines[0].account_id and not line.reconciled)
        return lines.reconcile()

    def get_account_move_line(self, line_id):
        lines = self.env['account.move.line'].browse(line_id)
        payment = lines.move_id.payment_id
        if payment.detraction and self.l10n_pe_dte_is_detraction:
            payment.write({'date':  self.invoice_date})
            write_off_amount_currency = payment.amount
            if payment.payment_type == 'outbound':
                write_off_amount_currency *= -1
            liquidity_amount_currency, liquidity_balance, write_off_balance,  counterpart_amount_currency, counterpart_balance, currency_id = payment._prepare_vals_debit_credit_amount_currency(write_off_amount_currency)
            # !

            outstanding_line = payment.line_ids.filtered(lambda r: r.account_id == payment.outstanding_account_id.id)
            destination_line = payment.line_ids.filtered(lambda r: r.account_id == payment.destination_account_id.id)
            
            # Liquidity line.
            outstanding_data = {
                'date_maturity': payment.date,
                'amount_currency': liquidity_amount_currency,
                'currency_id': currency_id,
                'debit': liquidity_balance if liquidity_balance > 0.0 else 0.0,
                'credit': -liquidity_balance if liquidity_balance < 0.0 else 0.0,

            }
            # Receivable / Payable.
            destination_data = {
                'date_maturity': payment.date,
                'amount_currency': counterpart_amount_currency,
                'currency_id': currency_id,
                'debit': counterpart_balance if counterpart_balance > 0.0 else 0.0,
                'credit': -counterpart_balance if counterpart_balance < 0.0 else 0.0,
            }

            outstanding_line.write(outstanding_data)
            destination_line.write(destination_data)
       
            # !
            # new_data = {
            #     'liquidity_amount_currency': liquidity_amount_currency,
            #     'liquidity_balance': liquidity_balance,
            #     'write_off_balance': write_off_balance,
            #     'counterpart_amount_currency': counterpart_amount_currency,
            #     'counterpart_balance': counterpart_balance,
            #     'currency_id': currency_id,
            # }
            # payment.write(new_data)
        elif payment.detraction  and not self.l10n_pe_dte_is_detraction:
            UserError('Está tratando de pagar con un pago de detracción una factura que no es de detracción.')
        return lines
   

    # def js_assign_outstanding_line(self, line_id):
    #     ''' Called by the 'payment' widget to reconcile a suggested journal item to the present
    #     invoice.

    #     :param line_id: The id of the line to reconcile with the current invoice.
    #     '''
    #     self.ensure_one()
    #     lines = self.env['account.move.line'].browse(line_id)
    #     lines += self.line_ids.filtered(lambda line: line.account_id == lines[0].account_id and not line.reconciled)
    #     move = self
    #     if not self.l10n_pe_dte_is_detraction or move.move_type not in ('out_invoice', 'in_invoice'):
    #         return super().js_assign_outstanding_line(line_id)
    #     else:
    #         journal = self._get_detraction_journal()
    #         lines = lines.filtered(lambda line: line.move_id != move)
    #         if move.move_type == 'out_invoice':
    #             detraction_no_reconciciled_lines = lines.filtered(lambda line: line.journal_id == journal)
    #         elif move.move_type == 'in_invoice':
    #             detraction_no_reconciciled_lines = lines.filtered(lambda line: line.payment_id.payment_method_line_id.name == 'Detracciones')
    #         no_detraction_no_reconciciled_lines = lines - detraction_no_reconciciled_lines

    #         # * Búsqueda de pagos
    #         detraction_reconciciled_lines, no_detraction_reconciciled_lines = self._get_detraction_reconciled_move_lines(journal)

    #         detraction_lines = detraction_no_reconciciled_lines | detraction_reconciciled_lines
    #         no_detraction_lines = no_detraction_no_reconciciled_lines | no_detraction_reconciciled_lines

    #         # * Calculo de límites
    #         # ! j.payment_id and en ambs filtered de abajo retirado
    #         detraction_amount_pay = abs(sum(detraction_lines.mapped(lambda a: a.move_id.amount_total_signed)))  # * Viene con moneda de la empresa
    #         no_detraction_amount_pay = abs(sum(no_detraction_lines.mapped(lambda a: a.move_id.amount_total_signed)))  # * Viene con moneda de la empresa
    #         # detraction_amount = self.l10n_pe_dte_detraction_amount  # * Viene con moneda de la factura (fuente)
    #         # no_detraction_amount = self.amount_total - detraction_amount  # * Viene con moneda de la factura (fuente)
    #         detraction_amount, no_detraction_amount = self._get_detraction_amount()

    #         if (not tools.float_is_zero(detraction_amount - detraction_amount_pay, precision_rounding=1) and detraction_amount < detraction_amount_pay) or (not tools.float_is_zero(no_detraction_amount - no_detraction_amount_pay, precision_rounding=1) and no_detraction_amount < no_detraction_amount_pay):
    #             raise UserError('No tiene permitido conciliar estos montos, verifique el monto de pago destinado a detracción.')
    #         return super().js_assign_outstanding_line(line_id)

    def _get_reconciled_move_lines(self):
        """Helper used to retrieve the reconciled move line on this journal entry"""
        reconciled_lines = self.line_ids.filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
        reconciled_amls = reconciled_lines.mapped('matched_debit_ids.debit_move_id') + \
            reconciled_lines.mapped('matched_credit_ids.credit_move_id')
        return reconciled_amls

    def _get_info_aml_detraction(self, reconciled_amls, journal=False):
        self.warning_detraction_journal(journal)
        if self.move_type == 'out_invoice':
            detraction_reconciciled_lines = reconciled_amls.filtered(lambda line: line.journal_id == journal)
        elif self.move_type == 'in_invoice':
            detraction_reconciciled_lines = reconciled_amls.filtered(lambda line: line.payment_id.payment_method_line_id.name == 'Detracciones')
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
        detraction_amount = self.l10n_pe_dte_detraction_amount  # * Viene con moneda de la empresa
        no_detraction_amount = abs(self.amount_total_signed) - detraction_amount
        return detraction_amount, no_detraction_amount

    def _get_detraction_journal(self):
        return self.env.user.company_id.detraction_journal_id
