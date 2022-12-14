
from odoo import models, fields, api, _


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'
    _description = 'Register Payment'

    # @api.depends('can_edit_wizard')
    # def _compute_group_payment(self):
    #     super(AccountPaymentRegister, self)._compute_group_payment()
    #     for wizard in self:
    #         if wizard.can_edit_wizard and wizard.group_payment:
    #             batches = wizard._get_batches()
    #             wizard.group_payment = len(batches[0]['lines'].move_id) == 1
    #         else:
    #             wizard.group_payment = False

    # @api.depends('line_ids')
    def _compute_from_lines(self):
        ''' Load initial values from the account.moves passed through the context. '''
        for wizard in self:
            batches = wizard._get_batches()
            batch_result = batches[0]

            company = batch_result['lines'].company_id
            wizard_values_from_batch = wizard._get_wizard_values_from_batch(batch_result)

            detraction = list(filter(lambda b: b.get('lines').account_id == company.detraction_outbound_account_id, batches))

            if len(batches) == 1 or (len(batches) == 2 and len(detraction) == 1):
                # == Single batch to be mounted on the view ==
                wizard.update(wizard_values_from_batch)

                wizard.can_edit_wizard = True
                wizard.can_group_payments = len(batch_result['lines']) != 1
            else:
                # == Multiple batches: The wizard is not editable  ==
                wizard.update({
                    'company_id': batches[0]['lines'][0].company_id.id,
                    'partner_id': False,
                    'partner_type': False,
                    'payment_type': wizard_values_from_batch['payment_type'],
                    'source_currency_id': False,
                    'source_amount': False,
                    'source_amount_currency': False,
                })

                wizard.can_edit_wizard = False
                wizard.can_group_payments = any(len(batch_result['lines']) != 1 for batch_result in batches)
