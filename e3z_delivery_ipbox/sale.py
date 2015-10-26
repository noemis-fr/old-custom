# -*- coding: utf-8 -*-
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-2013 Elanz (<http://www.openelanz.fr>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

__author__ = 'vchemiere'

from openerp.osv import osv, fields
import time
from openerp.tools.translate import _
from openerp.addons.delivery import sale


def delivery_set_2(self, cr, uid, ids, context=None):
        order_obj = self.pool.get('sale.order')
        line_obj = self.pool.get('sale.order.line')
        grid_obj = self.pool.get('delivery.grid')
        carrier_obj = self.pool.get('delivery.carrier')
        acc_fp_obj = self.pool.get('account.fiscal.position')
        for order in self.browse(cr, uid, ids, context=context):
            grid_id = carrier_obj.grid_get(cr, uid, [order.carrier_id.id], order.partner_shipping_id.id)
            if not grid_id:
                raise osv.except_osv(_('No Grid Available!'), _('No grid matching for this carrier!'))

            if not order.state in ('draft'):
                raise osv.except_osv(_('Order not in Draft State!'), _('The order state have to be draft to add delivery lines.'))

            grid = grid_obj.browse(cr, uid, grid_id, context=context)

            taxes = grid.carrier_id.product_id.taxes_id
            fpos = order.fiscal_position or False
            taxes_ids = acc_fp_obj.map_tax(cr, uid, fpos, taxes)
            #create the sale order line
            line_obj.create(cr, uid, {
                'order_id': order.id,
                'name': grid.carrier_id.name,
                'product_uom_qty': 1,
                'product_uom': grid.carrier_id.product_id.uom_id.id,
                'product_id': grid.carrier_id.product_id.id,
                'price_unit': grid_obj.get_price(cr, uid, grid.id, order, time.strftime('%Y-%m-%d'), context),
                'tax_id': [(6,0,taxes_ids)],
                'type': 'make_to_stock'
            })
        #remove the value of the carrier_id field on the sale order
        # return self.write(cr, uid, ids, {'carrier_id': False}, context=context)
        return {'type': 'ir.actions.act_window_close'} #action reload?

sale.sale_order.delivery_set = delivery_set_2


class sale_order(osv.osv):

    _inherit = 'sale.order'

    def create(self, cr, uid, vals, context=None):
        if vals.get('carrier_id', False):
            order_obj = self.pool.get('sale.order')
            line_obj = self.pool.get('sale.order.line')
            grid_obj = self.pool.get('delivery.grid')
            carrier_obj = self.pool.get('delivery.carrier')
            acc_fp_obj = self.pool.get('account.fiscal.position')

            carrier_id = vals.get('carrier_id', False)
            partner_shipping_id = vals.get('partner_shipping_id', False)
            grid_id = carrier_obj.grid_get(cr, uid, [carrier_id], partner_shipping_id)
            if not grid_id:
                raise osv.except_osv(_('No Grid Available!'), _('No grid matching for this carrier!'))

            # if not order.state in ('draft'):
            #     raise osv.except_osv(_('Order not in Draft State!'), _('The order state have to be draft to add delivery lines.'))

            grid = grid_obj.browse(cr, uid, grid_id, context=context)

            taxes = grid.carrier_id.product_id.taxes_id
            # fpos = order.fiscal_position or False
            fpos = vals.get('fiscal_position', False)
            taxes_ids = acc_fp_obj.map_tax(cr, uid, fpos, taxes)

            total = 0
            subtotal = 0
            weight = 0
            volume = 0
            for line in vals.get('abstract_line_ids', []):
                if line[2]['product_id']:
                    product = self.pool.get('product.product').browse(cr, uid, line[2]['product_id'])
                    if not line[2]['product_id']:
                        continue
                    subtotal = line[2]['price_unit'] * line[2]['product_uom_qty']
                    total += subtotal - (line[2]['discount'] * subtotal / 100)  or 0.0
                    weight += (product.weight or 0.0) * line[2]['product_uom_qty']
                    volume += (product.volume or 0.0) * line[2]['product_uom_qty']


            grid_obj.get_price_from_picking(cr, uid, grid.id, total,weight, volume, context=context)

            #create the sale order line
            line_vals = {
                'name': grid.carrier_id.name,
                'product_uom_qty': 1,
                'product_uom': grid.carrier_id.product_id.uom_id.id,
                'product_id': grid.carrier_id.product_id.id,
                # 'price_unit': grid_obj.get_price(cr, uid, grid.id, order, time.strftime('%Y-%m-%d'), context),
                # 'price_unit': 100.0,
                'tax_id': [(6,0,taxes_ids)],
                'type': 'make_to_stock'
            }
            # vals['abstract_line_ids'] = vals.get('abstract_line_ids') + [0, False, line_vals]
            vals.get('abstract_line_ids').append([0, False, line_vals])
        order_id = super(sale_order, self).create(cr, uid, vals, context)
        if vals.get('carrier_id', False):
            order = self.pool.get('sale.order').browse(cr, uid, order_id)
            price_unit = grid_obj.get_price(cr, uid, grid.id, order, time.strftime('%Y-%m-%d'), context),
            for line in order.abstract_line_ids:
                if line.product_id.id == grid.carrier_id.product_id.id:
                    self.pool.get('sale.order.line').write(cr, uid, line.id, {'price_unit': price_unit[0]})
        return order_id

    def write(self, cr, uid, ids, vals, context=None):
        if type(ids) == int:
            ids = [ids]
        for order in self.pool.get('sale.order').browse(cr, uid, ids):
            carrier_id = vals.get('carrier_id', False)

            if carrier_id:
                no_carrier = True
                carrier = self.pool.get('delivery.carrier').browse(cr, uid, carrier_id)
                for line in order.order_line:
                    if carrier.product_id.id == line.product_id.id:
                        no_carrier = False

                if no_carrier:
                    line_obj = self.pool.get('sale.order.line')
                    grid_obj = self.pool.get('delivery.grid')
                    carrier_obj = self.pool.get('delivery.carrier')
                    acc_fp_obj = self.pool.get('account.fiscal.position')

                    grid_id = carrier_obj.grid_get(cr, uid, [carrier_id], order.partner_shipping_id.id)
                    if not grid_id:
                        raise osv.except_osv(_('No Grid Available!'), _('No grid matching for this carrier!'))

                    if not order.state in ('draft'):
                        raise osv.except_osv(_('Order not in Draft State!'), _('The order state have to be draft to add delivery lines.'))

                    grid = grid_obj.browse(cr, uid, grid_id, context=context)

                    taxes = grid.carrier_id.product_id.taxes_id
                    fpos = order.fiscal_position or False
                    taxes_ids = acc_fp_obj.map_tax(cr, uid, fpos, taxes)
                    #create the sale order line
                    line_obj.create(cr, uid, {
                        'order_id': order.id,
                        'name': grid.carrier_id.name,
                        'product_uom_qty': 1,
                        'product_uom': grid.carrier_id.product_id.uom_id.id,
                        'product_id': grid.carrier_id.product_id.id,
                        'price_unit': grid_obj.get_price(cr, uid, grid.id, order, time.strftime('%Y-%m-%d'), context),
                        'tax_id': [(6,0,taxes_ids)],
                        'type': 'make_to_stock'
                    })
        return super(sale_order, self).write(cr, uid, ids, vals, context)