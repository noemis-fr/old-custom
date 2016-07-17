# -*- coding: utf-8 -*-
# Copyright (C) 2012-2013 Elanz (<http://www.openelanz.fr>).
# @author: rguillot
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.osv import orm, fields


class AccountInvoiceLine(orm.Model):
    _inherit = 'account.invoice.line'

    # Invalidation Section
    def _get_invoice_line_by_product(self, cr, uid, ids, context=None):
        """ids are product.product"""
        return self.pool['account.invoice.line'].search(
            cr, uid, [('product_id', 'in', ids)], context=context)

    def _get_invoice_line_by_invoice(self, cr, uid, ids, context=None):
        """ids are account.invoice"""
        return self.pool['account.invoice.line'].search(
            cr, uid, [('invoice_id', 'in', ids)], context=context)

    def _get_invoice_line_by_sale_order(self, cr, uid, ids, context=None):
        """ids are sale.order"""
        orders = self.browse(cr, uid, ids, context=context)
        order_names = [order.name for order in orders]
        return self.pool['account.invoice.line'].search(
            cr, uid, [('origin_so', 'in', order_names)], context=context)

    # Compute Section
    def _get_date_info(self, cr, uid, ids, fields, arg, context=None):
        res = {x: {'month': False, 'year': False} for x in ids}
        for line in self.browse(cr, uid, ids, context=context):
            if line.invoice_id.date_invoice:
                date_invoice = datetime.strptime(
                    line.invoice_id.date_invoice, DEFAULT_SERVER_DATE_FORMAT)
                res[line.id] = {
                    'month': date_invoice.month,
                    'year': date_invoice.year,
                }
        return res

    def _get_origin_so(self, cr, uid, ids, fields, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            origin_so = False
            if line.origin:
                for origin in line.origin.split(':'):
                    if len(origin) > 3 and origin[:2] == 'SO':
                        origin_so = origin
            res[line.id] = origin_so
        return res

    def _get_project_code_so(self, cr, uid, ids, fields, arg, context=None):
        order_obj = self.pool['sale.order']
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            if line.origin_so:
                order_ids = order_obj.search(
                    cr, uid, [('name', '=', line.origin_so)], context=context)
                if order_ids:
                    order = order_obj.browse(
                        cr, uid, order_ids[0], context=context)
                    res[line.id] = order.project_code
        return res

    _columns = {
        # Invoice Related
        'type': fields.related(
            'invoice_id', 'type', string='Type', type='char', store=True),
        'ref_invoice': fields.related(
            'invoice_id', 'number', string='Ref Invoice', type='char',
            store={
                'account.invoice': (
                    _get_invoice_line_by_invoice, ['number', 'state'], 10),
            }),

        # Sale Order Related
        'origin_so': fields.function(
            _get_origin_so, string='SO', type='char', store={
                'account.invoice.line': (
                    lambda self, cr, uid, ids, c=None: ids, ['origin'], 10),
            }),

        'project_code_so': fields.function(
            _get_project_code_so, string='Project Code', type='char', store={
                'account.invoice.line': (
                    lambda self, cr, uid, ids, c=None: ids, ['origin'], 20),
                'sale.order': (
                    _get_invoice_line_by_sale_order, ['project_code'], 50),
            }),

        # Date Related
        'date_invoice': fields.related(
            'invoice_id', 'date_invoice', string='Date invoice', type='date',
            store={
                'account.invoice': (
                    _get_invoice_line_by_invoice, ['date_invoice'], 10),
            }),
        'month': fields.function(
            _get_date_info, type='char', string='Month',
            multi='date_info', store={
                'account.invoice': (
                    _get_invoice_line_by_invoice, ['date_invoice'], 10),
            }),
        'year': fields.function(
            _get_date_info, type='char', string='Year',
            multi='date_info', store={
                'account.invoice': (
                    _get_invoice_line_by_invoice, ['date_invoice'], 10),
            }),

        # Period Related
        'period_id': fields.related(
            'invoice_id', 'period_id', string='Period',
            relation='account.period', type='many2one', store={
                'account.invoice': (
                    _get_invoice_line_by_invoice, ['period_id'], 10),
            }),

        # Product Related
        'ref_product': fields.related(
            'product_id', 'default_code', string='Ref product', type='char',
            store={
                'account.invoice.line': (
                    lambda self, cr, uid, ids, c=None: ids, ['product_id'],
                    10),
                'product.product': (
                    _get_invoice_line_by_product, ['default_code'], 10),
            }),
        'category': fields.related(
            'product_id', 'categ_id', string='Category',
            relation='product.category', type='many2one', store={
                'account.invoice.line': (
                    lambda self, cr, uid, ids, c=None: ids, ['product_id'],
                    10),
                'product.product': (
                    _get_invoice_line_by_product, ['categ_id'], 10),
            }),
    }
