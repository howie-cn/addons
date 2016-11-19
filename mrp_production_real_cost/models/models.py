# -*- coding: utf-8 -*-

import time

from openerp.osv import osv
from openerp.tools import float_is_zero
from openerp.tools.translate import _


class mrp_production(osv.osv):
    _inherit = 'mrp.production'

    def _calculate_total_cost(self, cr, uid, total_consume_moves, context=None):
        total_cost = 0
        for consumed_move in self.pool['stock.move'].browse(cr, uid, total_consume_moves, context=context):
            total_cost += sum([x.inventory_value for x in consumed_move.quant_ids if x.qty > 0])
        return total_cost

    def _calculate_workcenter_cost(self, cr, uid, production_id, context=None):
        """ Compute the planned production cost from the workcenters """
        production = self.browse(cr, uid, production_id, context=context)
        total_cost = 0.0
        for wc_line in production.workcenter_lines:
            wc = wc_line.workcenter_id
            total_cost += wc_line.hour * wc.costs_hour + wc_line.cycle * wc.costs_cycle

        return total_cost

    def action_produce(self, cr, uid, production_id, production_qty, production_mode, wiz=False, context=None):
        """ To produce final product based on production mode (consume/consume&produce).
        If Production mode is consume, all stock move lines of raw materials will be done/consumed.
        If Production mode is consume & produce, all stock move lines of raw materials will be done/consumed
        and stock move lines of final product will be also done/produced.
        @param production_id: the ID of mrp.production object
        @param production_qty: specify qty to produce in the uom of the production order
        @param production_mode: specify production mode (consume/consume&produce).
        @param wiz: the mrp produce product wizard, which will tell the amount of consumed products needed
        @return: True
        """
        stock_mov_obj = self.pool.get('stock.move')
        uom_obj = self.pool.get("product.uom")
        production = self.browse(cr, uid, production_id, context=context)
        production_qty_uom = uom_obj._compute_qty(cr, uid, production.product_uom.id, production_qty, production.product_id.uom_id.id)
        precision = self.pool['decimal.precision'].precision_get(cr, uid, 'Product Unit of Measure')

        main_production_move = False
        if production_mode == 'consume_produce':
            for produce_product in production.move_created_ids:
                if produce_product.product_id.id == production.product_id.id:
                    main_production_move = produce_product.id

        total_consume_moves = set()
        if production_mode in ['consume', 'consume_produce']:
            if wiz:
                consume_lines = []
                for cons in wiz.consume_lines:
                    consume_lines.append({'product_id': cons.product_id.id, 'lot_id': cons.lot_id.id, 'product_qty': cons.product_qty})
            else:
                consume_lines = self._calculate_qty(cr, uid, production, production_qty_uom, context=context)
            for consume in consume_lines:
                remaining_qty = consume['product_qty']
                for raw_material_line in production.move_lines:
                    if raw_material_line.state in ('done', 'cancel'):
                        continue
                    if remaining_qty <= 0:
                        break
                    if consume['product_id'] != raw_material_line.product_id.id:
                        continue
                    consumed_qty = min(remaining_qty, raw_material_line.product_qty)
                    stock_mov_obj.action_consume(cr, uid, [raw_material_line.id], consumed_qty, raw_material_line.location_id.id,
                                                 restrict_lot_id=consume['lot_id'], consumed_for=main_production_move, context=context)
                    total_consume_moves.add(raw_material_line.id)
                    remaining_qty -= consumed_qty
                if not float_is_zero(remaining_qty, precision_digits=precision):
                    # consumed more in wizard than previously planned
                    product = self.pool.get('product.product').browse(cr, uid, consume['product_id'], context=context)
                    extra_move_id = self._make_consume_line_from_data(cr, uid, production, product, product.uom_id.id, remaining_qty, context=context)
                    stock_mov_obj.write(cr, uid, [extra_move_id], {'restrict_lot_id': consume['lot_id'],
                                                                    'consumed_for': main_production_move}, context=context)
                    stock_mov_obj.action_done(cr, uid, [extra_move_id], context=context)
                    total_consume_moves.add(extra_move_id)

        if production_mode == 'consume_produce':
            # add production lines that have already been consumed since the last 'consume & produce'
            last_production_date = production.move_created_ids2 and max(production.move_created_ids2.mapped('date')) or False
            already_consumed_lines = production.move_lines2.filtered(lambda l: l.date > last_production_date)
            total_consume_moves = total_consume_moves.union(already_consumed_lines.ids)

            price_unit = 0
            for produce_product in production.move_created_ids:
                is_main_product = (produce_product.product_id.id == production.product_id.id) and production.product_id.cost_method == 'real'
                if is_main_product:
                    total_cost = self._calculate_total_cost(cr, uid, list(total_consume_moves), context=context)
                    production_cost = self._calculate_workcenter_cost(cr, uid, production_id, context=context)
                    price_unit = (total_cost + production_cost) / production_qty_uom

                subproduct_factor = self._get_subproduct_factor(cr, uid, production.id, produce_product.id, context=context)
                lot_id = False
                if wiz:
                    lot_id = wiz.lot_id.id
                qty = min(subproduct_factor * production_qty_uom, produce_product.product_qty)  # Needed when producing more than maximum quantity
                if is_main_product and price_unit:
                    stock_mov_obj.write(cr, uid, [produce_product.id], {'price_unit': price_unit}, context=context)
                new_moves = stock_mov_obj.action_consume(cr, uid, [produce_product.id], qty,
                                                         location_id=produce_product.location_id.id, restrict_lot_id=lot_id, context=context)
                stock_mov_obj.write(cr, uid, new_moves, {'production_id': production_id}, context=context)
                remaining_qty = subproduct_factor * production_qty_uom - qty
                if not float_is_zero(remaining_qty, precision_digits=precision):
                    # In case you need to make more than planned
                    # consumed more in wizard than previously planned
                    extra_move_id = stock_mov_obj.copy(cr, uid, produce_product.id, default={'product_uom_qty': remaining_qty,
                                                                                             'production_id': production_id}, context=context)
                    if is_main_product:
                        stock_mov_obj.write(cr, uid, [extra_move_id], {'price_unit': price_unit}, context=context)
                    stock_mov_obj.action_confirm(cr, uid, [extra_move_id], context=context)
                    stock_mov_obj.action_done(cr, uid, [extra_move_id], context=context)

        self.message_post(cr, uid, production_id, body=_("%s produced") % self._description, context=context)

        # Remove remaining products to consume if no more products to produce
        if not production.move_created_ids and production.move_lines:
            stock_mov_obj.action_cancel(cr, uid, [x.id for x in production.move_lines], context=context)

        self.signal_workflow(cr, uid, [production_id], 'button_produce_done')
        return True
