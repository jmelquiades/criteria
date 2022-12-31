# -*- coding: utf-8 -*-
# from odoo import http


# class CrmExtended(http.Controller):
#     @http.route('/crm_extended/crm_extended', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/crm_extended/crm_extended/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('crm_extended.listing', {
#             'root': '/crm_extended/crm_extended',
#             'objects': http.request.env['crm_extended.crm_extended'].search([]),
#         })

#     @http.route('/crm_extended/crm_extended/objects/<model("crm_extended.crm_extended"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('crm_extended.object', {
#             'object': obj
#         })
