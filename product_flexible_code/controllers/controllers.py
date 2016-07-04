# -*- coding: utf-8 -*-
from openerp import http

# class ProductFlexibleCode(http.Controller):
#     @http.route('/product_flexible_code/product_flexible_code/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/product_flexible_code/product_flexible_code/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('product_flexible_code.listing', {
#             'root': '/product_flexible_code/product_flexible_code',
#             'objects': http.request.env['product_flexible_code.product_flexible_code'].search([]),
#         })

#     @http.route('/product_flexible_code/product_flexible_code/objects/<model("product_flexible_code.product_flexible_code"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('product_flexible_code.object', {
#             'object': obj
#         })