# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2012 OpenERP SA (<http://openerp.com>).
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
##############################################################################

from openerp.osv import osv, fields
from openerp.osv.orm import browse_record, browse_null
from openerp import netsvc
from openerp.tools.translate import _
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP

import logging 

_logger = logging.getLogger(__name__)

class purchase_order_line(osv.osv):
    _inherit = 'purchase.order.line'
    
    _columns = {
        'origin' : fields.char(string='Origine')
    }   
    
class stock_move(osv.osv):
    _inherit = 'stock.move'
    _columns = {
        'purchase_origin': fields.related('purchase_line_id','origin', type='char', string='Origin Merged', readonly=True),
        
    }


    
class purchase_order(osv.osv):
    _inherit = 'purchase.order'

    _columns = {
        'order_line': fields.one2many('purchase.order.line', 'order_id', 'Order Lines'),
    }

    def do_merge(self, cr, uid, ids, context=None):
        """
        To merge similar type of purchase orders.
        Orders will only be merged if:
        * Purchase Orders are in draft
        * Purchase Orders belong to the same partner
        * Purchase Orders are have same stock location, same pricelist
        Lines will only be merged if:
        * Order lines are exactly the same except for the quantity and unit

         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param ids: the ID or list of IDs
         @param context: A standard dictionary

         @return: new purchase order id

        """
        # TOFIX: merged order line should be unlink
        wf_service = netsvc.LocalService("workflow")
        def make_key(br, fields):
            list_key = []
            for field in fields:
                field_val = getattr(br, field)
                if field in ('product_id', 'move_dest_id', 'account_analytic_id'):
                    if not field_val:
                        field_val = False
                if isinstance(field_val, browse_record):
                    field_val = field_val.id
                elif isinstance(field_val, browse_null):
                    field_val = False
                elif isinstance(field_val, list):
                    field_val = ((6, 0, tuple([v.id for v in field_val])),)
                list_key.append((field, field_val))
            list_key.sort()
            return tuple(list_key)

        # Compute what the new orders should contain

        new_orders = {}

        for porder in [order for order in self.browse(cr, uid, ids, context=context) if order.state == 'draft']:
            order_key = make_key(porder, ('partner_id', 'location_id', 'pricelist_id'))
            new_order = new_orders.setdefault(order_key, ({}, []))
            new_order[1].append(porder.id)
            order_infos = new_order[0]
            if not order_infos:
                order_infos.update({
                    'origin': porder.origin,
                    'date_order': porder.date_order,
                    'partner_id': porder.partner_id.id,
                    'dest_address_id': porder.dest_address_id.id,
                    'warehouse_id': porder.warehouse_id.id,
                    'location_id': porder.location_id.id,
                    'pricelist_id': porder.pricelist_id.id,
                    'payment_term_id': porder.payment_term_id.id,
                    'state': 'draft',
                    'order_line': {},
                    'notes': '%s' % (porder.notes or '',),
                    'fiscal_position': porder.fiscal_position and porder.fiscal_position.id or False,
                })
            else:
                if porder.date_order < order_infos['date_order']:
                    order_infos['date_order'] = porder.date_order
                if porder.notes:
                    order_infos['notes'] = (order_infos['notes'] or '') + ('\n%s' % (porder.notes,))
                if porder.origin:
                    order_infos['origin'] = (order_infos['origin'] or '') + ' ' + porder.origin

            for order_line in porder.order_line:
                line_key = make_key(order_line, ('name', 'date_planned', 'taxes_id', 'price_unit', 'product_id', 'move_dest_id', 'account_analytic_id'))
                o_line = order_infos['order_line'].setdefault(line_key, {})
                _logger.debug("O_LINE %s" % o_line)
                if o_line:
                    # merge the line with an existing line
                    o_line['product_qty'] += order_line.product_qty * order_line.product_uom.factor / o_line['uom_factor']
                else:
                    # append a new "standalone" line
                    for field in ('product_qty', 'product_uom'):
                        field_val = getattr(order_line, field)
                        if isinstance(field_val, browse_record):
                            field_val = field_val.id
                        o_line[field] = field_val
                    o_line['uom_factor'] = order_line.product_uom and order_line.product_uom.factor or 1.0
                o_line['origin'] = order_line.origin or order_line.order_id.origin or ''
                _logger.debug("O_LINE %s" % o_line)


        allorders = []
        orders_info = {}
        for order_key, (order_data, old_ids) in new_orders.iteritems():
            # skip merges with only one order
            if len(old_ids) < 2:
                allorders += (old_ids or [])
                continue

            # cleanup order line data
            for key, value in order_data['order_line'].iteritems():
                del value['uom_factor']
                value.update(dict(key))
            order_data['order_line'] = [(0, 0, value) for value in order_data['order_line'].itervalues()]

            # create the new order
            neworder_id = self.create(cr, uid, order_data)
            orders_info.update({neworder_id: old_ids})
            allorders.append(neworder_id)

            # make triggers pointing to the old orders point to the new order
            for old_id in old_ids:
                wf_service.trg_redirect(uid, 'purchase.order', old_id, neworder_id, cr)
                wf_service.trg_validate(uid, 'purchase.order', old_id, 'purchase_cancel', cr)
        return orders_info

    def write(self, cr, uid, ids, vals, context=None):
        """
        Modification du price_unit dans la facture si changement sur la ligne d'achat correspondate
        :param cr:
        :param uid:
        :param ids:
        :param vals: must containt new price_unit value of an order_line
        :param context:
        :return:
        """
        for purchase in self.pool.get('purchase.order').browse(cr, uid, ids):
            order_lines = vals.get('order_line', False)
            if order_lines:
                for line_vals in order_lines:
                    if purchase.state != 'draft' and (line_vals[0] == 0 or line_vals[0] == 2):
                        raise osv.except_osv(_('Error!'), _('You cannot create or delete purchase line when the order is approved.'))

        return super(purchase_order, self).write(cr, uid, ids, vals, context)

    def action_cancel_draft(self, cr, uid, ids, context=None):
        res = super(purchase_order, self).action_cancel_draft(cr, uid, ids, context)
        for purchase in self.browse(cr, uid, ids):
            for line in purchase.order_line:
                line.write({'state':'draft'})
        return res
    
    def wkf_confirm_order(self, cr, uid, ids, context=None):
        res = super(purchase_order, self).wkf_confirm_order(cr, uid, ids, context)
        for purchase in self.browse(cr, uid, ids, context=context):
            if purchase.origin and ('PLANIFICATEUR' in purchase.origin or purchase.origin.startswith('SO')):
                purchase.write({'date_order': datetime.now().strftime('%Y-%m-%d')})
        return res

class procurement_order(osv.osv):
    _inherit = 'procurement.order'

    def _get_purchase_schedule_date(self, cr, uid, procurement, company, context=None):
        """Return the datetime value to use as Schedule Date (``date_planned``) for the
           Purchase Order Lines created to satisfy the given procurement.
    
           :param browse_record procurement: the procurement for which a PO will be created.
           :param browse_report company: the company to which the new PO will belong to.
           :rtype: datetime
           :return: the desired Schedule Date for the PO lines
        """
        procurement_date_planned = datetime.strptime(procurement.date_planned, DEFAULT_SERVER_DATETIME_FORMAT)
        schedule_date = (procurement_date_planned)
        return schedule_date
    
    def _get_purchase_order_date(self, cr, uid, procurement, company, schedule_date, context=None):
        """Return the datetime value to use as Order Date (``date_order``) for the
           Purchase Order created to satisfy the given procurement.
    
           :param browse_record procurement: the procurement for which a PO will be created.
           :param browse_report company: the company to which the new PO will belong to.
           :param datetime schedule_date: desired Scheduled Date for the Purchase Order lines.
           :rtype: datetime
           :return: the desired Order Date for the PO
        """
        return schedule_date

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: