# -*- coding: utf-8 -*-

from . import controllers
from . import models
from odoo import api, SUPERUSER_ID, _

def _update_company(env):
    """ Este hook es usado para setear True al validador de
    RUC/DNI cuando el módulo addcri_partner_rucsearch está
    instalado."""
    
    company_ids = env['res.company'].search([]).filtered(lambda r: r.country_id.code == 'PE')
    company_ids.write({'l10n_pe_rucsearch': True})
    
def _addcri_rucsearch_init(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _update_company(env)
