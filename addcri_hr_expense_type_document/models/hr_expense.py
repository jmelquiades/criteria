# -*- coding: utf-8 -*-
from odoo.exceptions import UserError, ValidationError
from odoo import models, fields,api,_
from datetime import datetime, timedelta,date,time
from dateutil.relativedelta import relativedelta

class HrExpense(models.Model):
    _inherit= 'hr.expense'
    l10n_latam_document_type_id = fields.Many2one(
        'l10n_latam.document.type','Document Type',required=True,
    
    )
    igv = fields.Monetary('IGV')
    rc = fields.Monetary('RC')
    redondeo = fields.Monetary('Redondeo')
    
    def action_submit_expenses(self, **kwargs):
        """Validate igv"""
        documents = {}
        if self.total_amount <=0:
            raise UserError('El total debe ser mayor a cero')
        if self.igv:
            if self.igv > 0 and self.total_amount > 0:
                total_pagar=self.total_amount
                igv=self.igv
                rc=self.rc
                base=total_pagar - igv -rc
                valor=(igv*100)/float(base)
                porcentaje_igv=round(valor,0)
                obj_taxes = self.env['account.tax'].search([('amount','=',porcentaje_igv),(('type_tax_use','=','purchase')),(('price_include','=',True))])
                if obj_taxes:
                    print(len(self.tax_ids.ids))
                    if len(self.tax_ids.ids)==0:
                        self.tax_ids=obj_taxes
                else:
                    raise UserError('El valor del igv ingresado no corresponde al 10% y/o  18%')
                    
        return super(HrExpense, self).action_submit_expenses(**kwargs)


    # onchange igv *********
    @api.onchange('igv','rc')
    def onchange_igv(self):
        if self.igv:
            if self.igv > 0 and self.total_amount > 0:
                total_pagar=self.total_amount
                igv=self.igv
                rc=self.rc
                base=total_pagar - igv -rc 
                valor=(igv*100)/float(base)
                porcentaje_igv=round(valor,0)
                obj_taxes = self.env['account.tax'].search([('amount','=',porcentaje_igv),(('type_tax_use','=','purchase')),(('price_include','=',True))])
                if obj_taxes:
                    self.tax_ids=obj_taxes
                else:
                    self.tax_ids=False
    # override this method *********
    def _prepare_move_values(self):
        """
        This function prepares move values related to an expense
        """
        self.ensure_one()
        journal = self.sheet_id.bank_journal_id if self.payment_mode == 'company_account' else self.sheet_id.journal_id
        account_date = self.sheet_id.accounting_date or self.date

        sequense='/'
        if journal:
            obj_account_journal = self.env['account.journal'].search([('id', '=', journal.id)])
            obj_sequence=obj_account_journal['sequence_seat']
            if not obj_sequence:
                raise ValidationError(("Por favor, establezca la secuencia del asiento contable en el diario %s:\n%s") % (obj_account_journal['name'],'(Localización PERU - Secuencia del Asiento)'))
            else:
                if obj_sequence.use_date_range:
                    self._validate_sequence_date_range(obj_sequence)

            if journal.type=='purchase':
                # if not self.posted_before:
                sequense=obj_sequence.next_by_code(obj_sequence.code)
            
        move_values = {
            'journal_id': journal.id,
            'company_id': self.sheet_id.company_id.id,
            'date': account_date,
            'ref': self.sheet_id.name,
            'l10n_latam_document_type_id':self.l10n_latam_document_type_id,
            # force the name to the default value, to avoid an eventual 'default_name' in the context
            # to set it to '' which cause no number to be given to the account.move when posted.
            'name': sequense
        }
        return move_values
    def _get_account_move_line_values(self):
        move_line_values_by_expense = {}
        for expense in self:
            move_line_name = expense.employee_id.name + ': ' + expense.name.split('\n')[0][:64]
            account_src = expense._get_expense_account_source()
            account_dst = expense._get_expense_account_destination()
            account_date = expense.sheet_id.accounting_date or expense.date or fields.Date.context_today(expense)

            company_currency = expense.company_id.currency_id

            move_line_values = []
            # Hquilla mod. 23.02.2023
            total_rc=expense.rc
            total_redondeo=expense.redondeo
            unit_amount = expense.unit_amount or expense.total_amount
            unit_amount=unit_amount - total_rc 

            quantity = expense.quantity if expense.unit_amount else 1
            taxes = expense.tax_ids.with_context(round=True).compute_all(unit_amount, expense.currency_id,quantity,expense.product_id)
            total_amount = 0.0
            total_amount_currency = 0.0
            partner_id = expense.employee_id.sudo().address_home_id.commercial_partner_id.id

            # source move line
            balance = expense.currency_id._convert(taxes['total_excluded'], company_currency, expense.company_id, account_date)
            amount_currency = taxes['total_excluded']
            move_line_src = {
                'name': move_line_name,
                'quantity': expense.quantity or 1,
                'debit': balance if balance > 0 else 0,
                'credit': -balance if balance < 0 else 0,
                'amount_currency': amount_currency,
                'account_id': account_src.id,
                'product_id': expense.product_id.id,
                'product_uom_id': expense.product_uom_id.id,
                'analytic_account_id': expense.analytic_account_id.id,
                'analytic_tag_ids': [(6, 0, expense.analytic_tag_ids.ids)],
                'expense_id': expense.id,
                'partner_id': partner_id,
                'tax_ids': [(6, 0, expense.tax_ids.ids)],
                'tax_tag_ids': [(6, 0, taxes['base_tags'])],
                'currency_id': expense.currency_id.id,
            }
            move_line_values.append(move_line_src)
            total_amount -= balance
            total_amount_currency -= move_line_src['amount_currency']

            # taxes move lines
            for tax in taxes['taxes']:
                balance = expense.currency_id._convert(tax['amount'], company_currency, expense.company_id, account_date)
                amount_currency = tax['amount']

                if tax['tax_repartition_line_id']:
                    rep_ln = self.env['account.tax.repartition.line'].browse(tax['tax_repartition_line_id'])
                    base_amount = self.env['account.move']._get_base_amount_to_display(tax['base'], rep_ln)
                    base_amount = expense.currency_id._convert(base_amount, company_currency, expense.company_id, account_date)
                else:
                    base_amount = None

                move_line_tax_values = {
                    'name': tax['name'],
                    'quantity': 1,
                    'debit': balance if balance > 0 else 0,
                    'credit': -balance if balance < 0 else 0,
                    'amount_currency': amount_currency,
                    'account_id': tax['account_id'] or move_line_src['account_id'],
                    'tax_repartition_line_id': tax['tax_repartition_line_id'],
                    'tax_tag_ids': tax['tag_ids'],
                    'tax_base_amount': base_amount,
                    'expense_id': expense.id,
                    'partner_id': partner_id,
                    'currency_id': expense.currency_id.id,
                    'analytic_account_id': expense.analytic_account_id.id if tax['analytic'] else False,
                    'analytic_tag_ids': [(6, 0, expense.analytic_tag_ids.ids)] if tax['analytic'] else False,
                }
                total_amount -= balance
                total_amount_currency -= move_line_tax_values['amount_currency']
                move_line_values.append(move_line_tax_values)
            
            
            # RECARGO POR CONSUMO
            if  total_rc > 0:
                total_amount -= total_rc
                total_amount_currency -= total_rc
                move_line_rc = {
                    'name': 'Recargo al Consumo',
                    'quantity': 1,
                    'debit': total_rc,
                    'credit': 0,
                    'amount_currency': total_rc,
                    'account_id': account_src.id,
                    'tax_base_amount': base_amount,
                    'expense_id': expense.id,
                    'partner_id': partner_id,
                    'currency_id': expense.currency_id.id
                }
                print('----:',move_line_rc)
                move_line_values.append(move_line_rc)

            # REDONDEO
            if  total_redondeo > 0:
                total_amount -=  total_redondeo
                total_amount_currency -=  total_redondeo
                move_line_redondeo = {
                    'name': 'Dscto Redondeo',
                    'quantity': 1,
                    'debit': total_redondeo,
                    'credit': 0,
                    'amount_currency': total_redondeo,
                    'account_id': account_src.id,
                    'tax_base_amount': base_amount,
                    'expense_id': expense.id,
                    'partner_id': partner_id,
                    'currency_id': expense.currency_id.id
                }
                print('----:',move_line_redondeo)
                move_line_values.append(move_line_redondeo)

            # destination move line

            move_line_dst = {
                    'name': move_line_name,
                    'debit': total_amount > 0 and total_amount,
                    'credit': total_amount < 0 and -total_amount,
                    'account_id': account_dst,
                    'date_maturity': account_date,
                    'amount_currency': total_amount_currency,
                    'currency_id': expense.currency_id.id,
                    'expense_id': expense.id,
                    'partner_id': partner_id,
                    'exclude_from_invoice_tab': True,
                }
            move_line_values.append(move_line_dst)
            
            move_line_values_by_expense[expense.id] = move_line_values
        return move_line_values_by_expense

    def _validate_sequence_date_range(self,obj_sequence):
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

    def create_expense_from_attachments(self, attachment_ids=None, view_type='tree'):
            ''' Create the expenses from files.
            :return: An action redirecting to hr.expense tree view.
            '''
            if attachment_ids is None:
                attachment_ids = []
            attachments = self.env['ir.attachment'].browse(attachment_ids)
            if not attachments:
                raise UserError(_("No attachment was provided"))
            expenses = self.env['hr.expense']

            if any(attachment.res_id or attachment.res_model != 'hr.expense' for attachment in attachments):
                raise UserError(_("Invalid attachments!"))

            product = self.env['product.product'].search([('can_be_expensed', '=', True)])
            if product:
                product = product.filtered(lambda p: p.default_code == "EXP_GEN") or product[0]
            else:
                raise UserError(_("You need to have at least one category that can be expensed in your database to proceed!"))

            typedocument = self.env['l10n_latam.document.type'].search([('use_in_expense', '=', True)])

            if typedocument:
                 id_typedocument =typedocument.ids[0]
            else:
                 id_typedocument =False
            for attachment in attachments:
                
                expense = self.env['hr.expense'].create({
                    'name': attachment.name.split('.')[0],
                    'unit_amount': 0,
                    'product_id': product.id,
                    'l10n_latam_document_type_id':id_typedocument
                })
                attachment.write({
                    'res_model': 'hr.expense',
                    'res_id': expense.id,
                })
                attachment.register_as_main_attachment()
                expenses += expense
            return {
                'name': _('Generated Expenses'),
                'res_model': 'hr.expense',
                'type': 'ir.actions.act_window',
                'views': [[False, view_type], [False, "form"]],
                'context': {'search_default_my_expenses': 1, 'search_default_no_report': 1},
            }