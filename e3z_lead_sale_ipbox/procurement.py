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


class procurement_order(osv.osv):
    _inherit = 'procurement.order'

    _columns = {
        'message': fields.char('Latest error', size=512, help="Exception occurred while computing procurement orders."),
    }

    # def create_automatic_op(self, cr, uid, context=None):
    #     """
    #     Create procurement of  virtual stock < 0
    #
    #     @param self: The object pointer
    #     @param cr: The current row, from the database cursor,
    #     @param uid: The current user ID for security checks
    #     @param context: A standard dictionary for contextual values
    #     @return:  Dictionary of values
    #     """
    #     obj_data = self.pool.get('ir.model.data')
    #     shop_id = obj_data.get_object_reference(cr, uid, 'sale', 'sale_shop_1')[1],
    #     context['shop'] = shop_id
    #     res = super(procurement_order, self).create_automatic_op(cr, uid, context)
    #     return res
