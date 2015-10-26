# -*- coding: utf-8 -*-
##############################################################################
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
##############################################################################

__author__ = 'vvayssiere'

from osv import fields, osv
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from openerp.addons.procurement import procurement

class procurement_order(osv.osv):
    _inherit = "procurement.order"
    
    def _prepare_automatic_op_procurement(self, cr, uid, product, warehouse, location_id, context=None):
        vals = super(procurement_order, self)._prepare_automatic_op_procurement(cr, uid, product, warehouse, location_id, context=context)
        vals['origin'] = self._get_op_orders(cr, uid, product, location_id, context=context)
        return vals
    
    def _get_op_orders(self, cr, uid, product, location_id, context=None):
        states = ('confirmed','waiting','assigned','done') 
        what =  ('in', 'out')
        
        from_date = context.get('from_date', False)
        to_date = context.get('to_date', False)
        date_str = False
        date_values = False
        location_ids = [location_id]
        ids = [product.id]
        where = [tuple(location_ids),tuple(location_ids),tuple(ids),tuple(states)]
        if from_date and to_date:
            date_str = "date>=%s and date<=%s"
            where.append(tuple([from_date]))
            where.append(tuple([to_date]))
        elif from_date:
            date_str = "date>=%s"
            date_values = [from_date]
        elif to_date:
            date_str = "date<=%s"
            date_values = [to_date]
        if date_values:
            where.append(tuple(date_values))
    
        prodlot_id = context.get('prodlot_id', False)
        prodlot_clause = ''
        if prodlot_id:
            prodlot_clause = ' and prodlot_id = %s '
            where += [prodlot_id]
        
        if 'out' in what:
            # all moves from a location in the set to a location out of the set
            cr.execute(
                'select distinct origin '\
                'from stock_move '\
                'where location_id IN %s '\
                'and location_dest_id NOT IN %s '\
                'and product_id  IN %s '\
                'and state in %s ' + (date_str and 'and '+date_str+' ' or '') + ' '\
                + prodlot_clause + 
                'order by origin',tuple(where))
            results2 = cr.fetchall()
        originStr = ''
#         for origin in results:
#             originStr += origin[0] + ' / '
        # Count the outgoing quantities
        for origin in results2:
            originStr += origin[0] + ' / '
        return originStr[:-3]
