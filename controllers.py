# -*- coding: utf-8 -*-
from openerp import http

# class AuthOauthExtended(http.Controller):
#     @http.route('/auth_oauth_extended/auth_oauth_extended/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/auth_oauth_extended/auth_oauth_extended/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('auth_oauth_extended.listing', {
#             'root': '/auth_oauth_extended/auth_oauth_extended',
#             'objects': http.request.env['auth_oauth_extended.auth_oauth_extended'].search([]),
#         })

#     @http.route('/auth_oauth_extended/auth_oauth_extended/objects/<model("auth_oauth_extended.auth_oauth_extended"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('auth_oauth_extended.object', {
#             'object': obj
#         })