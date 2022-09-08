# -*- coding: utf-8 -*-
# from odoo import http


# class PePartnerMobsuruc(http.Controller):
#     @http.route('/pe_partner_mobsuruc/pe_partner_mobsuruc', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pe_partner_mobsuruc/pe_partner_mobsuruc/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('pe_partner_mobsuruc.listing', {
#             'root': '/pe_partner_mobsuruc/pe_partner_mobsuruc',
#             'objects': http.request.env['pe_partner_mobsuruc.pe_partner_mobsuruc'].search([]),
#         })

#     @http.route('/pe_partner_mobsuruc/pe_partner_mobsuruc/objects/<model("pe_partner_mobsuruc.pe_partner_mobsuruc"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pe_partner_mobsuruc.object', {
#             'object': obj
#         })
