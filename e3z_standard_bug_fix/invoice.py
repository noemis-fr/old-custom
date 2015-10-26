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

__author__ = 'melhadjmimoune'

from openerp.osv import osv, fields


class account_invoice(osv.osv):
    _inherit = "account.invoice"
    def confirm_paid(self, cr, uid, ids, context=None):
        ok = super(account_invoice,self).confirm_paid(cr, uid, ids, context=context)
        if ok:
            cr.execute("""SELECT DISTINCT rel.order_id FROM sale_order_invoice_rel rel
                                            WHERE rel.invoice_id = ANY(%s)""", (list(ids),))
            order_ids = [i[0] for i in cr.fetchall()]
            if order_ids:
                sale_obj = self.pool.get('sale.order')
                sale_line_obj = self.pool.get('sale.order.line')

                order_to_update =[]
                for order in sale_obj.browse(cr,uid, order_ids,context):
                    if order.invoiced and order.shipped:
                        order_to_update.append(order.id)
                if order_to_update:
                    sale_obj.write(cr, uid, order_to_update, {'state':'done'}, context=context)
        return ok
