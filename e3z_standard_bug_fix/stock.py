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
from openerp.addons.sale_stock import stock as sale_stock
from openerp.addons.stock import stock
import time

class stock_picking(osv.osv):
    _inherit = "stock.picking"

def _invoice_hook_service_invoiced(self, cursor, user, picking, invoice_id):
    sale_obj = self.pool.get('sale.order')
    order_line_obj = self.pool.get('sale.order.line')
    invoice_obj = self.pool.get('account.invoice')
    invoice_line_obj = self.pool.get('account.invoice.line')
    if picking.sale_id:
        sale_obj.write(cursor, user, [picking.sale_id.id], {
            'invoice_ids': [(4, invoice_id)],
            })
        for sale_line in picking.sale_id.order_line:
            if sale_line.product_id.type == 'service' and not sale_line.invoiced:
                vals = order_line_obj._prepare_order_line_invoice_line(cursor, user, sale_line, False)
                vals['invoice_id'] = invoice_id
                invoice_line_id = invoice_line_obj.create(cursor, user, vals)
                order_line_obj.write(cursor, user, [sale_line.id], {
                    'invoice_lines': [(6, 0, [invoice_line_id])],'invoiced':True,
                    })

                invoice_obj.button_compute(cursor, user, [invoice_id])
    return True

sale_stock.stock_picking._invoice_hook = _invoice_hook_service_invoiced

def action_done_order_done(self, cr, uid, ids, context=None):
    """Changes picking state to done.

    This method is called at the end of the workflow by the activity "done".
    @return: True
    """
    self.write(cr, uid, ids, {'state': 'done', 'date_done': time.strftime('%Y-%m-%d %H:%M:%S')})
    sale_obj = self.pool.get('sale.order')
    # wf_service = netsvc.LocalService("workflow")

    for pik in self.browse(cr,uid, ids,context):
        if pik.sale_id:
            other_pik_not_done = self.search(cr, uid, [
                ('sale_id', '=', pik.sale_id.id),('state','!=','done')], limit=1000, context=context)
            if not other_pik_not_done:
                if pik.sale_id.invoiced:
                    sale_obj.write(cr, uid, [pik.sale_id.id], {'state': 'done', 'shipped': True})
                else:
                    sale_obj.write(cr, uid, [pik.sale_id.id], {'shipped': True})


    return True

stock.stock_picking.action_done = action_done_order_done