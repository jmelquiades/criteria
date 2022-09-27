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

    @api.constrains('l10n_pe_dte_detraction_percent', 'l10n_pe_dte_is_detraction')
    def _constrains_l10n_pe_dte_detraction_percent(self):
        if self.l10n_pe_dte_is_detraction and not self.l10n_pe_dte_detraction_code:
            raise UserError('Definir el tipo de detracción')

    @api.onchange('invoice_line_ids', 'l10n_pe_dte_detraction_percent')
    def _onchange_detraction_percent(self):
        self._recompute_tax_lines()
        super(AccountMove, self)._onchange_detraction_percent()
        self.l10n_pe_dte_detraction_amount = math.ceil(self.l10n_pe_dte_detraction_amount)
