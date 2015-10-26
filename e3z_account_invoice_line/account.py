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
from openerp.tools.translate import _
from openerp.addons.account import account
from openerp.tools.float_utils import float_round
import openerp.addons.decimal_precision as dp


class account_invoice_line(osv.osv):
    _inherit = 'account.invoice.line'

    def _get_month(self, cr, uid, ids, fields, arg, context=None):
        res = {}
        for id in ids:
            order = self.browse(cr, uid, id)
            if order.date_invoice:
                res[id] = order.date_invoice.split('-')[1]
        return res

    def _get_year(self, cr, uid, ids, fields, arg, context=None):
        res = {}
        for id in ids:
            order = self.browse(cr, uid, id)
            if order.date_invoice:
                res[id] = order.date_invoice.split('-')[0]
        return res

    def _get_origin_so(self, cr, uid, ids, fields, arg, context=None):
        res = {}
        for order_line in self.browse(cr, uid, ids):
            if order_line.origin:
                origin_so = False
                for origin in order_line.origin.split(':'):
                    if len(origin) > 3 and origin[:2] == 'SO':
                        origin_so = origin
                res[order_line.id] = origin_so
        return res

    _columns = {
        'date_invoice': fields.related('invoice_id', 'date_invoice', string='Date invoice', type='date', store=True),
        'type': fields.related('invoice_id', 'type', string='Type', type='char', store=True),
        'ref_invoice': fields.related('invoice_id', 'number', string='Ref invoice', type='char', store=True),
        'ref_product': fields.related('product_id', 'default_code', string='Ref product', type='char', store=True),
        'month': fields.function(_get_month, type="char", string="Month", store=True),
        'year': fields.function(_get_year, type="char", string="Year", store=True),
        'period_id': fields.related('invoice_id', 'period_id', string='Period', relation="account.period",
                                    type='many2one', store=True),
        'category': fields.related('product_id', 'categ_id', string='Category', relation="product.category",
                                    type='many2one', store=True),
        'origin_so': fields.function(_get_origin_so, type="char", string="SO", store=True)
    }