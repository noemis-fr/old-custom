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

from openerp.osv import osv
from openerp.tools.translate import _


class sale_order(osv.osv):
    _inherit = 'sale.order'

    def force_done(self, cr, uid, ids, context=None):
        paid = True

        name = self.read(cr, uid, ids[0], ['name'])['name']

        # invoice = self.pool.get('account.invoice').search(cr, uid, [('origin', 'like', name), ('type', '=', 'out_invoice')])
        # if invoice:
        #     invoice = self.pool.get('account.invoice').read(cr, uid, invoice[0], ['state'])
        #     if invoice and invoice['state'] == 'paid':
        #         paid = True
        # if not paid:
        #     raise osv.except_osv(_('Error!'), _('You cannot terminate an order which have not been paid.'))

        stocks_picking = self.pool.get('stock.picking.out').search(cr, uid, [('origin', '=', name)])
        for stock_picking in stocks_picking:
            stock = self.pool.get('stock.picking.out').read(cr, uid, stock_picking, ['state'])
            if stock and stock['state'] not in ['done', 'cancel']:
                raise osv.except_osv(_('Error!'), _('You cannot terminate an order which have at less one stock picking which is not terminated / cancelled.'))
        shipped = True

        if paid and shipped:
            self.write(cr, uid, ids, {'state': 'done'})

        return True