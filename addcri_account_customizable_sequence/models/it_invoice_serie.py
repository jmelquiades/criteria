# -*- coding: utf-8 -*-
# from odoo import models, fields, api

from odoo import models, fields, api

class account_Extend_Report(models.Model):
    _name = 'it.invoice.serie'
    _description = "Configuracion de Secuencia Por tipo de documento "

    
    name = fields.Char(string='Name' ,required=True)
    type_document = fields.Many2one('l10n_latam.document.type', string='Type document', required=True)
    sequence = fields.Many2one('ir.sequence', string='Sequence', required=True)

    is_manual = fields.Boolean(string='Is Manual')
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True, default=lambda self: self.env.company)
    
    

