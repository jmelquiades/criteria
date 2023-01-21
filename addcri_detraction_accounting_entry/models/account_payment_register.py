
from odoo import models, fields, api, _


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'
    _description = 'Register Payment'

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


    def _create_payment_vals_from_wizard(self):
        payment_vals = super(AccountPaymentRegister, self)._create_payment_vals_from_wizard()
        if self.payment_method_line_id.name == 'Detracciones':
            payment_vals.update(
                {
                'destination_account_id': self.company_id.detraction_outbound_account_id.id
                }
            )
        return payment_vals

    def _create_payments(self):
        self.ensure_one()
        batches = self._get_batches()
        edit_mode = self.can_edit_wizard and (len(batches[0]['lines']) == 1 or self.group_payment)
        to_process = []

        if edit_mode:
            payment_vals = self._create_payment_vals_from_wizard()
            data = {
                'create_vals': payment_vals,
                'batch': batches[0],
            }
            if self.payment_method_line_id.name == 'Detracciones':
                data.update({
                    'to_reconcile': sorted(batches, key=lambda r: self.company_id.detraction_outbound_account_id in r.get('lines', []).mapped('account_id'), reverse=True)[0]['lines']
                })
            else:
                data.update({
                    'to_reconcile': batches[0]['lines'],
                })
            to_process.append(data)
        else:
            # Don't group payments: Create one batch per move.
            if not self.group_payment:
                new_batches = []
                for batch_result in batches:
                    for line in batch_result['lines']:
                        new_batches.append({
                            **batch_result,
                            'payment_values': {
                                **batch_result['payment_values'],
                                'payment_type': 'inbound' if line.balance > 0 else 'outbound'
                            },
                            'lines': line,
                        })
                batches = new_batches

            for batch_result in batches:
                to_process.append({
                    'create_vals': self._create_payment_vals_from_batch(batch_result),
                    'to_reconcile': batch_result['lines'],
                    'batch': batch_result,
                })

        payments = self._init_payments(to_process, edit_mode=edit_mode)
        self._post_payments(to_process, edit_mode=edit_mode)
        self._reconcile_payments(to_process, edit_mode=edit_mode)
        return payments