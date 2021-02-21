# -*- coding: utf-8 -*-
# from odoo import http


# class Batgame(http.Controller):
#     @http.route('/batgame/batgame/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/batgame/batgame/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('batgame.listing', {
#             'root': '/batgame/batgame',
#             'objects': http.request.env['batgame.batgame'].search([]),
#         })

#     @http.route('/batgame/batgame/objects/<model("batgame.batgame"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('batgame.object', {
#             'object': obj
#         })
