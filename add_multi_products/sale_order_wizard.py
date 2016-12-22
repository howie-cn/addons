# -*- coding: utf-8 -*-
from openerp import models, fields, api
from datetime import date, datetime


class sale_order_add_multiple(models.TransientModel):
    _name = 'sale.order.add_multiple'
    _description = 'Sale order add multiple'

    quantity = fields.Float(u'批量设置数量',
                            default='1.0')
    products_ids = fields.Many2many(
        'product.product',
        string=u'产品',
        domain=[('sale_ok', '=', True)],
    )

    @api.one
    def add_multiple(self):
        active_id = self._context['active_id']
        sale_flag = self._context['sale_flag']

        if sale_flag:
            sale = self.env['sale.order'].browse(active_id)
            for product_id in self.products_ids:
                product = self.env['product.product'].sudo().browse(product_id.id)
                val = {
                    'name': product.name,
                    'product_type': product.product_type,
                    'default_code': product.default_code,
                    'product_name': product.name,
                    'product_uom_qty': self.quantity,
                    'order_id': active_id,
                    'product_id': product_id.id or False,
                    'product_uom': product_id.uom_id.id,
                    'price_unit': product.price_unit_mem or product.list_price
                }
                self.env['sale.order.line'].create(val)
        else:
            purchase = self.env['purchase.order'].browse(active_id)
            for product_id in self.products_ids:
                product = self.env['product.product'].sudo().browse(product_id.id)
                val = {
                    'name': product.name,
                    'product_type': product.product_type,
                    'default_code': product.default_code,
                    'product_name': product.name,
                    'product_qty': self.quantity,
                    'order_id': active_id,
                    'product_id': product_id.id or False,
                    'product_uom': product_id.uom_id.id,
                    'price_unit': product.standard_price,
                    'date_planned': fields.Datetime.context_timestamp(self,datetime.now())
                }
                self.env['purchase.order.line'].create(val)
