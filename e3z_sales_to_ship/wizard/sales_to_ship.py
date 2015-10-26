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

__author__ = 'rguillot'

from openerp.osv import osv, fields


class sales_to_ship(osv.TransientModel):
    _name = 'sale.to.ship'

    def default_get(self, cr, uid, fields, context=None):
        res = super(sales_to_ship, self).default_get(cr, uid, fields, context=context)

        total = 0
        records = self.pool.get('stock.move').search(cr, uid, [('type', '=', 'out'),
                                                               ('state', 'not in', ['cancel', 'done'])], context=context)
        for line in self.pool.get('stock.move').browse(cr, uid, records):
            if line.sale_line_id:
                total += line.sale_line_id.price_unit * line.product_qty

        res.update({
            'amount_total': "%.2f€" % (total),
        })
        return res

    _columns = {
        'amount_total': fields.char("Total amount of orders not shipped", readonly=True)
    }
