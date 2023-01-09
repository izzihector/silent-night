# -*- coding: utf-8 -*-
# from odoo import http


# class SilentNightCustomization(http.Controller):
#     @http.route('/silent_night_customization/silent_night_customization', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/silent_night_customization/silent_night_customization/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('silent_night_customization.listing', {
#             'root': '/silent_night_customization/silent_night_customization',
#             'objects': http.request.env['silent_night_customization.silent_night_customization'].search([]),
#         })

#     @http.route('/silent_night_customization/silent_night_customization/objects/<model("silent_night_customization.silent_night_customization"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('silent_night_customization.object', {
#             'object': obj
#         })
