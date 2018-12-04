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
from openerp.tools.translate import _
from openerp.addons.account import account
from openerp.tools.float_utils import float_round
import openerp.addons.decimal_precision as dp


class account_invoice(osv.osv):

    _inherit = 'account.invoice'


    def _get_invoice(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('account.invoice.line').browse(cr, uid, ids, context=context):
            result[line.invoice_id.id] = True
        return result.keys()

    def _get_margin_percent(self, cr, uid, ids, field_name, arg, context):
        invoice_obj = self.pool.get('account.invoice')
        res = {}
        for invoice in invoice_obj.browse(cr, uid, ids):
            cost_total = 0
            cost_total = invoice.amount_untaxed
            if cost_total != 0:
                res[invoice.id] = invoice.margin * 100 / cost_total
            else:
                res[invoice.id] = 0
        return res

    def _product_margin(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            result[invoice.id] = 0.0
            for line in invoice.invoice_line:
                result[invoice.id] += line.margin or 0.0
        return result

    def _get_invoice_line(self, cr, uid, ids, context=None):
        line_ids = []
        for line in self.pool.get('account.invoice.line').browse(cr, uid, ids):
            line_ids.append(line.invoice_id.id)
        return line_ids


    _columns = {
     'margin': fields.function(_product_margin, string='Margin', help="It gives profitability by calculating the difference between the Unit Price and the cost price.", store={
         'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['distribution_costs'], 15),
         'account.invoice.line': (_get_invoice_line, ['price_unit', 'margin', 'purchase_price'], 11)
     }
     ),
     'margin_percent': fields.function(_get_margin_percent, type='float', string='Margin in Percent', store={
         'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['distribution_costs'], 16),
         'account.invoice.line': (_get_invoice_line, ['price_unit', 'margin', 'purchase_price'], 11)
     }),
     'distribution_costs': fields.float('Distribution costs'),
    'invoice_line': fields.one2many(
        'account.invoice.line', 'invoice_id', 'Invoice Lines'),
    }


class account_invoice_line(osv.osv):

    _inherit = 'account.invoice.line'

    def _get_margin_percent(self, cr, uid, ids, field_name, arg, context):
        invoice_line_obj = self.pool.get('account.invoice.line')
        res = {}
        for line in invoice_line_obj.browse(cr, uid, ids):
            res[line.id] = 0
            try:
                if line.quantity:
                    if line.price_unit == 0:
                        res[line.id] = round((line.quantity*(100.0-line.discount)/100.0) -(line.purchase_price*line.quantity), 2)
                        # res[line.id] = line.margin * 100 / (line.product_uom_qty)
                        res[line.id] -= line.quantity * (100.0-line.discount)/100 * (line.invoice_id.distribution_costs / 100.0)
                        divide = (line.quantity*((100.0-line.discount)/100.0))
                        if divide:
                            res[line.id] = res[line.id] * 100 / divide
                        else:
                            res[line.id] = 0
                    else:
                        # res[line.id] = line.margin * 100 / (line.price_unit * line.product_uom_qty)
                        res[line.id] = round((line.price_unit*line.quantity*(100.0-line.discount)/100.0) -(line.purchase_price*line.quantity), 2)
                        res[line.id] -= line.price_unit * line.quantity * (100.0-line.discount)/100 * (line.invoice_id.distribution_costs / 100.0)
                        res[line.id] = res[line.id] * 100 / (line.price_unit * line.quantity*((100.0-line.discount)/100.0))
            except:
                pass
        return res

    def _get_margin_display(self, cr, uid, ids, field_name, arg, context):
        invoice_line_obj = self.pool.get('account.invoice.line')
        res = {}
        precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
        for line in invoice_line_obj.browse(cr, uid, ids):
            if line.product_id:
                res[line.id] = str(line.margin or 0) + ' / ' + str(float_round(line.margin_percent, precision) or 0) + '%'
            else:
                res[line.id] = ''
        return res

    def _product_margin(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = 0
            try:
                if line.product_id:
                    if line.quantity:
                        res[line.id] = round((line.price_unit*line.quantity*(100.0-line.discount)/100.0) -(line.purchase_price*line.quantity), 2)
                    res[line.id] -= line.price_unit * line.quantity * (100.0-line.discount)/100 * (line.invoice_id.distribution_costs or 0) / 100.0
            except:
                pass
        return res

    def _get_invoice_line(self, cr, uid, ids, context=None):
        line_ids = []
        for id in ids:
            invoice = self.pool.get('account.invoice').browse(cr, uid, id)
            for line in invoice.invoice_line:
                line_ids.append(line.id)
        return line_ids

    _columns = {
        'margin_percent': fields.function(_get_margin_percent, type='float', string='Margin in Percent', digits_compute=dp.get_precision('Account')),
        'margin': fields.function(_product_margin, string='Margin', store={
            'account.invoice': (
                _get_invoice_line,
                ['distribution_costs'],
                10),
            'account.invoice.line': (
                lambda self, cr, uid, ids, c={}: ids,
                ['quantity', 'discount', 'purchase_price', 'price_unit'],
                10
            )
        }),
        'margin_display': fields.function(_get_margin_display, type='char', string='Margin'),
        'purchase_price': fields.float('CMUP', digits=(16,2), readonly=False),
        'status': fields.related('invoice_id', 'state', string='State', type='char', size=32),
    }

#def post2(self, cr, uid, ids, context=None):
#    if context is None:
#        context = {}
#    invoice = context.get('invoice', False)
#    valid_moves = self.validate(cr, uid, ids, context)
#
#    if not valid_moves:
#        raise osv.except_osv(_('Error!'), _('You cannot validate a non-balanced entry.\nMake sure you have configured payment terms properly.\nThe latest payment term line should be of the "Balance" type.'))
#    obj_sequence = self.pool.get('ir.sequence')
#    for move in self.browse(cr, uid, valid_moves, context=context):
#        if move.name =='/':
#            new_name = False
#            journal = move.journal_id
#
#            if invoice and invoice.internal_number:
#                new_name = invoice.internal_number
#            else:
#                if journal.sequence_id:
#                    c = {'fiscalyear_id': move.period_id.fiscalyear_id.id}
#                    new_name = obj_sequence.next_by_id(cr, uid, journal.sequence_id.id, c)
#                    prefix = u''
#                    if journal.type == 'sale':
#                        prefix = u'FV'
#                    elif journal.type == 'purchase':
#                        prefix = u'FF'
#                    if prefix and invoice:
#                        if not invoice.date_invoice:
#                            raise osv.except_osv(_('Error, no date!'),
#                                _('Please put a invoice date before validate this invoice.'))
#                        new_name = prefix + invoice.date_invoice[2:4] + invoice.date_invoice[5:7] + new_name
#                else:
#                    raise osv.except_osv(_('Error!'), _('Please define a sequence on the journal.'))
#
#            if new_name:
#                self.write(cr, uid, [move.id], {'name':new_name})
#
#    cr.execute('UPDATE account_move '\
#               'SET state=%s '\
#               'WHERE id IN %s',
#               ('posted', tuple(valid_moves),))
#    return True
#
#account.account_move.post = post2
