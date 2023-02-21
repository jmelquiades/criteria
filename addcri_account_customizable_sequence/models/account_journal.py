# -*- coding: utf-8 -*-
# from odoo import models, fields, api

from odoo import models, fields,api

class AccountJournal_Extended(models.Model):
    _inherit= 'account.journal'

    sequence_seat = fields.Many2one(
        'ir.sequence',
        'Secuencia del Asiento',
        required=True,
        # default=lambda self: self.env.ref('account_move_extended_hte.sequence_invoice_name')
        )
    
    register_sunat = fields.Char(
        string='Registro Sunat',
    )
    
    edit_number_seat = fields.Boolean(
        string='Editar Número Asiento',
    )
    use_in_surrenders = fields.Boolean(
        string='Se usa para Rendiciones',
    )
    
            
      
    
