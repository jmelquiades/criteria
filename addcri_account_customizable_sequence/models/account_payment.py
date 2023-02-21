# -*- coding: utf-8 -*-
from odoo.exceptions import UserError, ValidationError
from odoo import models, fields, api
from datetime import datetime, timedelta,date
from dateutil.relativedelta import relativedelta

class AccountPayment(models.Model):
    _inherit = "account.payment"

    def action_post(self):
        if not self.posted_before:
            obj_account_journal = self.env['account.journal'].search([('id', '=', self['journal_id'].id)])
            obj_sequence_bank=obj_account_journal['sequence_seat']
            if not obj_sequence_bank:
                raise ValidationError(("Por favor, establezca la secuencia del asiento contable en el diario %s:\n%s") % (obj_account_journal['name'],'(Localización PERU - Secuencia del Asiento)'))
            else:
                if obj_sequence_bank.use_date_range:
                    self._validate_sequence_date_range(obj_sequence_bank)

            sequense=obj_sequence_bank.next_by_code(obj_sequence_bank.code)
            self.name=sequense
        return super(AccountPayment, self).action_post()

        # --------------------------------------------------
    # METHODS VALIDATE  ir_sequence_date_range
    # --------------------------------------------------
    def _validate_sequence_date_range(self,obj_sequence):
        # self._validate_sequence_date_range()
                        today = fields.Date.today()
                        date_from=date(today.year, today.month, 1)
                        date_to = str(today + relativedelta(months=+1, day=1, days=-1))[:10]

                        seq_date = self.env['ir.sequence.date_range'].search(
                        [('sequence_id', '=', obj_sequence.id),
                         ('date_from', '>=', date_from), ('date_to', '<=', date_to)], limit=1)
                        if not seq_date:
                            #no date_range sequence was found, we create a new one
                            values = {
                                'date_from': date_from,
                                'date_to': date_to,
                                'sequence_id': obj_sequence.id
                            }
                            self.env['ir.sequence.date_range'].sudo().create(values)