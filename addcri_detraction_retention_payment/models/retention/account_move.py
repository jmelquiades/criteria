from odoo import _, api, fields, models
from odoo.exceptions import UserError

RETENTION_PAYMENT_STATE = [
    ('not_paid', 'No pagadas'),
    ('in_payment', 'En proceso de pago'),
    ('paid', 'Pagado'),
    ('partial', 'Pagado parcialmente'),
    ('unknown', 'No aplica'),
    # ('no_retention', 'No hay retención'),
]


class AccountMove(models.Model):
    _inherit = 'account.move'
    _description = 'Account Move'

    l10n_pe_dte_is_retention = fields.Boolean('Is retention?')
    retention_payment_state = fields.Selection(RETENTION_PAYMENT_STATE, string='Estado de pago de retención', compute='_get_retention_payment_state')

    @api.constrains('l10n_pe_dte_is_retention', 'l10n_pe_dte_retention_type')
    def _constrains_l10n_pe_dte_is_retention_l10n_pe_dte_retention_type(self):
        if self.l10n_pe_dte_is_retention and not self.l10n_pe_dte_retention_type:
            raise UserError('Debe elegir el tipo de retención.')

    @api.onchange('l10n_pe_dte_is_retention')
    def _onchange_l10n_pe_dte_is_retention(self):
        if self.l10n_pe_dte_is_retention == False:
            self.l10n_pe_dte_retention_type = False

    @api.onchange('l10n_pe_dte_operation_type')
    def _onchange_l10n_pe_dte_operation_type_retention(self):
        if self.l10n_pe_dte_operation_type in ['1001', '1002', '1003', '1004']:
            self.l10n_pe_dte_is_retention = False
            self.l10n_pe_dte_retention_type = False

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

    # ! test

    def action_register_payment(self):
        action = super().action_register_payment()
        if self.l10n_pe_dte_is_retention:
            action['context'].update(is_retention=True)
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
        if not self.l10n_pe_dte_is_retention:
            return super().js_assign_outstanding_line(line_id)
        else:
            journal = self._get_retention_journal()
            lines = lines.filtered(lambda line: line.move_id != move)
            retention_no_reconciciled_lines = lines.filtered(lambda line: line.journal_id == journal)
            no_retention_no_reconciciled_lines = lines - retention_no_reconciciled_lines

            # * Búsqueda de pagos
            retention_reconciciled_lines, no_retention_reconciciled_lines = self._get_retention_reconciled_move_lines(journal)

            retention_lines = retention_no_reconciciled_lines | retention_reconciciled_lines
            no_retention_lines = no_retention_no_reconciciled_lines | no_retention_reconciciled_lines

            # * Calculo de límites
            # ! j.payment_id and en ambs filtered de abajo retirado
            retention_amount_pay = abs(sum(retention_lines.mapped(lambda a: a.amount_currency)))  # * Viene con moneda del movimiento
            no_retention_amount_pay = abs(sum(no_retention_lines.mapped(lambda a: a.amount_currency)))  # * Viene con moneda del movimiento
            retention_amount, no_retention_amount = self._get_retention_amount()

            if retention_amount < retention_amount_pay or no_retention_amount < no_retention_amount_pay:
                raise UserError('No tiene permitido conciliar estos montos, verifique el monto de pago destinado a retención.')
            return super().js_assign_outstanding_line(line_id)
