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

from openerp.osv import fields, osv
from openerp.tools.translate import _


class sale_order(osv.osv):
    _inherit = 'sale.order'

    def action_button_confirm(self, cr, uid, ids, context=None):
        # fetch the partner's id and subscribe the partner to the sale order
        assert len(ids) == 1
        order = self.browse(cr, uid, ids[0], context=context)
        add_delivery_method = True
        only_service = True

        delivery_method = self.pool.get('delivery.carrier').search(cr, uid, [('default_in_sales', '=', True)])
        if delivery_method:
            delivery_method = self.pool.get('delivery.carrier').browse(cr, uid, delivery_method[0])
            if order.amount_untaxed < delivery_method.min_amount and not order.carrier_id:
                if order.partner_id.without_delivery:
                    add_delivery_method = False
                else:
                    for order_line in order.order_line:
                        if order_line.product_id:
                            if order_line.product_id.without_delivery:
                                add_delivery_method = False
                                break
                            elif order_line.product_id.type != 'service':
                                only_service = False

                if only_service:
                    add_delivery_method = False

                if add_delivery_method:
                    delivery_method = delivery_method.id
                    self.write(cr, uid, ids[0], {'carrier_id': delivery_method})

        return super(sale_order, self).action_button_confirm(cr, uid, ids, context=context)