# -*- coding: utf-8 -*-
# from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo import models, fields,api
from datetime import datetime, timedelta,date,time
from dateutil.relativedelta import relativedelta
class AccountMove_Extended(models.Model):
    
    _inherit= 'account.move'

    serie = fields.Many2one('it.invoice.serie','Serie',copy=False,)
    Serie_purchase  = fields.Char('Serie',copy=False,store=True) # serie compra
    voucher_number  = fields.Char('Voucher number',copy=False,store=True) # secuencia doc compra o venta

    type_journal = fields.Selection(related='journal_id.type')
    journal_id = fields.Many2one('account.journal',auto_join=True)
    sequence_ids = fields.Many2one('ir.sequence',related='serie.sequence', auto_join=True,store=False)
    sequence_id = fields.Integer(related='sequence_ids.id',store=False)
    next_sequence = fields.Char(store=False,copy=False)

    def get_default_invoice(self):
        if 'default_move_type' in self._context and self._context['default_move_type']=='out_invoice': 
            return datetime.today()
        else:
            return False

    invoice_date = fields.Date( default=get_default_invoice)
    name = fields.Char( compute=False, inverse=False,string='name', readonly=True,copy=False)

    @api.onchange('serie')
    def onchange_serie(self):
        if self.serie:
            sequence = self.env['ir.sequence'].search([('id','=',self.sequence_id)])
            next= sequence.get_next_char(sequence.number_next_actual)
            self.voucher_number=next

    # _inverse_l10n_latam_document_number set
    @api.onchange('l10n_latam_document_type_id', 'l10n_latam_document_number')
    def _inverse_l10n_latam_document_number(self):
        for rec in self.filtered(lambda x: x.l10n_latam_document_type_id):
            if not rec.l10n_latam_document_number:
                rec.name = '/'
                # rec.serie=''
            pass
        # super()._inverse_l10n_latam_document_number()

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        # OVERRIDE
        if len(self.ids)==0 and self.name==False:
           self.name ='/'
    # _inverse_l10n_latam_document_number set
    @api.onchange('l10n_latam_document_type_id')
    def _onchange_l10n_latam_document_type_id(self):
        # OVERRIDE
        if not self.posted_before and self.name=='/':
           self.serie=False
           self.Serie_purchase=''
           self.voucher_number=''

    
    def action_post(self):
        #inherit for modif. (sequence and serie)
            sequense=''
            sequense_serie=''
            if self['journal_id']:
                obj_account_journal = self.env['account.journal'].search([('id', '=', self['journal_id'].id)])
                obj_sequence=obj_account_journal['sequence_seat']
                if not obj_sequence:
                    raise ValidationError(("Por favor, establezca la secuencia del asiento contable en el diario %s:\n%s") % (obj_account_journal['name'],'(Localización PERU - Secuencia del Asiento)'))
                else:
                    if obj_sequence.use_date_range:
                        self._validate_sequence_date_range(obj_sequence)

                if self['journal_id'].type=='purchase':
                    if not self.posted_before:
                        sequense=obj_sequence.next_by_code(obj_sequence.code)
                    else:
                        sequense=self['name']    
                    sequense_serie=self['voucher_number']
                else:
                    if not self.posted_before:
                        sequense=obj_sequence.next_by_code(obj_sequence.code)
                        if self['serie']:
                            obj_serie= self.env['it.invoice.serie'].search([('id', '=', self['serie'].id)])
                            obj_sequence_serie = self.env['ir.sequence'].search([('id', '=', obj_serie.sequence.id)])
                            sequense_serie=obj_sequence_serie.next_by_code(obj_sequence_serie.code)
                    else:
                        sequense=self['name']
                        sequense_serie=self['voucher_number']

            self['name'] = sequense
            self['l10n_latam_document_number'] =  sequense_serie
            self['voucher_number'] = sequense_serie
            return super(AccountMove_Extended, self).action_post()
    
    # override this method comput *********
    @api.depends('journal_id', 'partner_id', 'company_id', 'move_type')
    def _compute_l10n_latam_available_document_types(self):
        self.l10n_latam_available_document_type_ids = False
        for rec in self.filtered(lambda x: x.journal_id and x.partner_id):
            rec.l10n_latam_available_document_type_ids = self.env['l10n_latam.document.type'].search(rec._get_l10n_latam_documents_domain())

    # override this method preview *********
    def preview_invoice(self):
        self.l10n_latam_document_number=self.voucher_number
        return super(AccountMove_Extended, self).preview_invoice()
    
    # override this method *********
    @api.model
    def _deduce_sequence_number_reset(self, name):
        if self.l10n_latam_use_documents or not self.l10n_latam_use_documents:
            return 'never'
        return super(self)._deduce_sequence_number_reset(name)
    
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