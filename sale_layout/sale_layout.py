# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields, osv
import decimal_precision as dp
from openerp.tools.translate import _


class sale_order_line(osv.osv):

    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        line_ids = []
        for id in ids:
            res[id] = 0.0
        for line in self.browse(cr, uid, ids, context=context):
            if line.layout_type == 'article' or line.layout_type == 'subtotal':
                line_ids.append(line.id)
        if line_ids:
            res_article = super(sale_order_line, self)._amount_line(cr, uid, line_ids, field_name, arg, context)
            res.update(res_article)
        return res

    def invoice_line_create(self, cr, uid, ids, context=None):
        new_ids = []
        list_seq = []
        for line in self.browse(cr, uid, ids, context=context):
            if line.layout_type == 'article':
                new_ids.append(line.id)
                list_seq.append(line.sequence)
        invoice_line_ids = super(sale_order_line, self).invoice_line_create(cr, uid, new_ids, context)
        pool_inv_line = self.pool.get('account.invoice.line')
        seq = 0
        for obj_inv_line in pool_inv_line.browse(cr, uid, invoice_line_ids, context=context):
            pool_inv_line.write(cr, uid, [obj_inv_line.id], {'sequence': list_seq[seq]}, context=context)
            seq += 1
        return invoice_line_ids

    def onchange_sale_order_line_view(self, cr, uid, id, type, context={}, *args):
        temp = {}
        temp['value'] = {}
        if (not type):
            return {}
        if type != 'article':

            temp = {
                'value': {
                'product_id': False,
                'uos_id': False,
                'account_id': False,
                'price_unit': 0.0,
                'price_subtotal': 0.0,
                'quantity': 0,
                'discount': 0.0,
                'invoice_line_tax_id': False,
                'account_analytic_id': False,
                'product_uom_qty': 0.0,
                },
            }
            if type == 'line':
                temp['value']['name'] = ' '
            if type == 'break':
                temp['value']['name'] = ' '
            if type == 'subtotal':
                temp['value']['name'] = _('Sub Total')
            return temp
        return {}

    def create(self, cr, user, vals, context=None):
        if vals.has_key('layout_type'):
            if vals['layout_type'] == 'line':
                vals['name'] = ' '
            if vals['layout_type'] == 'break':
                vals['name'] = ' '
            if vals['layout_type'] != 'article':
                vals['product_uom_qty']= 0
        return super(sale_order_line, self).create(cr, user, vals, context)

    def write(self, cr, user, ids, vals, context=None):
        if vals.has_key('layout_type'):
            if vals['layout_type'] == 'line':
                vals['name'] = ' '
            if vals['layout_type'] == 'break':
                vals['name'] = ' '

        return super(sale_order_line, self).write(cr, user, ids, vals, context)

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['layout_type'] = self.browse(cr, uid, id, context=context).layout_type
        default['sequence'] = self.browse(cr, uid, id, context=context).sequence
        return super(sale_order_line, self).copy(cr, uid, id, default, context)

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['layout_type'] = self.browse(cr, uid, id, context=context).layout_type
        default['sequence'] = self.browse(cr, uid, id, context=context).sequence
        return super(sale_order_line, self).copy_data(cr, uid, id, default, context)

    _order = "order_id, sequence asc"
    _description = "Sales Order line"
    _inherit = "sale.order.line"
    _columns = {
        'layout_type': fields.selection([
                ('article', 'Product'),
                ('title', 'Title'),
                ('text', 'Note'),
                ('subtotal', 'Sub Total'),
                # ('line', 'Separator Line'),
                ('break', 'Page Break'),]
            ,'Line Type', select=True, required=True, help="""
                This field determine the line display on sale edition.
                P: product, a classic line like standard
                T: title, a text in bold
                R: remark, simple text
                STl: subtotal, price subtotal of all lines above this
                SP: split page, a split for print.
            """),
        'sequence': fields.integer('Line Sequence', select=True),
        'price_unit': fields.float('Unit Price', required=True, digits_compute= dp.get_precision('Sale Price'), readonly=True, states={'draft': [('readonly', False)]}),
        'product_uom_qty': fields.float('Quantity (UoM)', digits_compute= dp.get_precision('Product UoS')),
        'product_uom': fields.many2one('product.uom', 'Product UoM'),
        # Override the field to call the overridden _amount_line function
        'price_subtotal': fields.function(_amount_line, method=True, string='Subtotal', digits_compute= dp.get_precision('Sale Price')),
    }

    _defaults = {
        'layout_type': 'article',
    }

sale_order_line()

class one2many_mod2(fields.one2many):
    def get(self, cr, obj, ids, name, user=None, offset=0, context=None, values=None):
        if not values:
            values = {}
        res = {}
        for id in ids:
            res[id] = []
        ids2 = obj.pool.get(self._obj).search(cr, user, [(self._fields_id, 'in', ids), ('layout_type', '=', 'article')], limit=self._limit)
        for r in obj.pool.get(self._obj)._read_flat(cr, user, ids2, [self._fields_id], context=context, load='_classic_write'):
            res[r[self._fields_id]].append( r['id'] )
        return res


class sale_order(osv.osv):

    def copy(self, cr, uid, id, default=None, context=None):
        if context is None:
            context = {}
        if default is None:
            default = {}
        default['order_line'] = False
        context.update({'from_copy': True})
        return super(sale_order, self).copy(cr, uid, id, default, context)

    _inherit = "sale.order"
    _columns = {
        'abstract_line_ids': fields.one2many('sale.order.line', 'order_id', 'Order Lines' ),
        'order_line': one2many_mod2('sale.order.line', 'order_id', 'Order Lines', readonly=True, states={'draft': [('readonly', False)]}),
    }

    def write(self, cr, user, ids, vals, context=None):
        subtotal = 0
        if vals.get('abstract_line_ids', False):
            seq = 0
            new_abstract_line_ids = []
            for line_vals in vals['abstract_line_ids']:
                if line_vals[0] == 0 or (line_vals[0] == 1 and line_vals[2]):
                    line_vals[2]['sequence'] = seq
                    new_abstract_line_ids.append(line_vals)
                elif line_vals[0] == 4:
                    self.pool.get('sale.order.line').write(cr, user, line_vals[1], {'sequence': seq})
                    new_abstract_line_ids.append(line_vals)
                else:
                    new_abstract_line_ids.append(line_vals)

                seq += 1

            vals['abstract_line_ids'] = new_abstract_line_ids
        res = super(sale_order, self).write(cr, user, ids, vals, context)
        for id in ids:
            order = self.pool.get('sale.order').browse(cr, user, id, context)
            line_ids = self.pool.get('sale.order.line').search(cr, user, [('order_id', '=', order.id)], order='sequence asc')
            for line_id in line_ids:
                line = self.pool.get('sale.order.line').browse(cr, user, line_id)
                if line.layout_type == 'subtotal':
                    line.write({'price_unit': subtotal, 'product_uom_qty': 1})
                    subtotal = 0
                elif line.layout_type == 'article':
                    subtotal += line.price_subtotal
        return res

    def create(self, cr, uid, vals, context=None):
        if vals.get('abstract_line_ids', False) and not context.get('from_copy', False):
            seq = 0
            new_abstract_line_ids = []
            for line_vals in vals['abstract_line_ids']:
                line_vals[2]['sequence'] = seq
                new_abstract_line_ids.append(line_vals)
                seq += 1
            vals['abstract_line_ids'] = new_abstract_line_ids
        res = super(sale_order, self).create(cr, uid, vals, context)
        subtotal = 0
        order = self.pool.get('sale.order').browse(cr, uid, res)
        line_ids = self.pool.get('sale.order.line').search(cr, uid, [('order_id', '=', order.id)], order='sequence asc')
        for line_id in line_ids:
            line = self.pool.get('sale.order.line').browse(cr, uid, line_id)
            if line.layout_type == 'subtotal':
                line.write({'price_unit': subtotal, 'product_uom_qty': 1})
                subtotal = 0
            elif line.layout_type == 'article':
                subtotal += line.price_subtotal
        return res

sale_order()

class stock_picking(osv.osv):
    _inherit = "stock.picking"

    def _prepare_invoice_line(self, cr, uid, group, picking, move_line, invoice_id, invoice_vals, context=None):
        vals = super(stock_picking, self)._prepare_invoice_line(cr, uid, group, picking, move_line, invoice_id, invoice_vals, context=context)

        if move_line.sale_line_id:
            vals['sequence'] = move_line.sale_line_id.sequence

        return vals

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
