from odoo import _, api, fields, models

class AccountPayment(models.Model):
    _inherit = 'account.payment'
    _description = 'Account Payment'
    
    @api.depends('journal_id', 'partner_id', 'partner_type', 'is_internal_transfer', 'payment_method_line_id')
    def _compute_destination_account_id(self):
        self.destination_account_id = False
        for pay in self:
            if pay.is_internal_transfer:
                pay.destination_account_id = pay.journal_id.company_id.transfer_account_id
            elif pay.partner_type == 'customer':
                # Receive money from invoice or send money to refund it.
                if pay.partner_id:
                    pay.destination_account_id = pay.partner_id.with_company(pay.company_id).property_account_receivable_id
                else:
                    pay.destination_account_id = self.env['account.account'].search([
                        ('company_id', '=', pay.company_id.id),
                        ('internal_type', '=', 'receivable'),
                        ('deprecated', '=', False),
                    ], limit=1)
            elif pay.partner_type == 'supplier':
                # Send money to pay a bill or receive money to refund it.
                if pay.partner_id:
                    if pay.payment_method_line_id.name == 'Detracciones':
                        pay.destination_account_id = pay.company_id.detraction_outbound_account_id
                    else:
                        pay.destination_account_id = pay.partner_id.with_company(pay.company_id).property_account_payable_id
                else:
                    pay.destination_account_id = self.env['account.account'].search([
                        ('company_id', '=', pay.company_id.id),
                        ('internal_type', '=', 'payable'),
                        ('deprecated', '=', False),
                    ], limit=1)