from odoo import _, api, fields, models
import base64
from odoo.exceptions import UserError


class AccountBatchPayment(models.Model):
    _inherit = 'account.batch.payment'
    _description = 'Account Batch Payment'

    arrival_journal_id = fields.Many2one('account.journal', string='Banco destino')
    txt_binary = fields.Binary('Txt Binary')
    txt_name = fields.Char('Txt Name')
    correlative_detraction_batch_payment = fields.Char('Correlativo de pago de detracción por lotes', default=lambda self: 'Nuevo')

    def generate_txt(self):
        values_content = self.get_data()
        self.txt_binary = base64.b64encode(
            values_content and values_content.encode() or '\n'.encode()
        )
        date = fields.Date.today()
        year = str(date.year)[-2:]
        correlative = self.correlative_detraction_batch_payment
        self.txt_name = f'D{self.env.user.company_id.vat[:11]}{year}{correlative}.txt'

    def get_data(self):
        company = self.env.user.company_id
        raw = f'*{company.vat}{company.name[:35]}'
        spaces = len(raw)
        raw += ' ' * (47 - spaces)
        date = fields.Date.today()
        if self.correlative_detraction_batch_payment == 'Nuevo':
            self.correlative_detraction_batch_payment = self.env['ir.sequence'].next_by_code('seq.detraction.batch.payment')
        correlative = self.correlative_detraction_batch_payment
        payment_without_moves = self.payment_ids.filtered(lambda p: not p.reconciled_bill_ids)
        if payment_without_moves:
            message = f'Los siguientes pagos no tienen factura vinculada:\n'
            for pwm in payment_without_moves:
                message += f'- {pwm.name}\n'
            raise UserError(message)
        amount_total = sum(self.payment_ids.mapped(lambda p: int(p.reconciled_bill_ids[0].l10n_pe_dte_detraction_amount)))
        amount_total = str(amount_total).zfill(13)
        year = str(date.year)[-2:]
        raw += f'{year}{correlative}{amount_total}00\r\n'

        for payment in self.payment_ids:
            move = payment.reconciled_bill_ids[0] if payment.reconciled_bill_ids else False
            if move:
                # move = payment.move_id
                partner = move.partner_id
                date = move.date
                line = f'{partner.l10n_latam_identification_type_id.l10n_pe_vat_code}{partner.vat[:35]}'
                spaces = len(line)
                service = move.l10n_pe_dte_detraction_code
                acc_number = payment.partner_bank_id.acc_number.replace('-', '')
                if len(acc_number) != 11:
                    raise UserError(f'El número de cuenta tiene {len(acc_number)} dígitos, debe de tener 11.')
                acc_number = acc_number[:11]
                op_code = '01'
                amount = str(int(move.l10n_pe_dte_detraction_amount)).zfill(13)
                prefix = move.sequence_prefix.split()[-1].replace('-', '')[:4]
                sequence = str(move.sequence_number)
                sequence = sequence.zfill(8) if len(sequence) < 8 else sequence[-8:]
                line += ' ' * (47 - spaces) + f'000000000{service}{acc_number}{amount}00{op_code}{date.year}{date.month}{move.l10n_latam_document_type_id.code}{prefix}{sequence}\r\n'
                raw += line
        return raw
