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
