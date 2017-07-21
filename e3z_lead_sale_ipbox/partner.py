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


class res_partner(osv.osv):
    _inherit = 'res.partner'

    def _compute_credit_info(self, cr, uid, ids, field_names, arg, context=None):
        order_obj = self.pool['sale.order']
        inv_obj = self.pool['account.invoice']
        res = super(res_partner, self)._credit_debit_get(
            cr, uid, ids, field_names, arg, context=context)
        for partner in self.browse(cr, uid, ids, context=context):
            # Get child partners
            child_ids = self.search(
                cr, uid, [('parent_id', '=', partner.id)], context=context)

            # Get uninvoiced sale orders
            sale_credit = 0
            inv_credit = 0
            order_ids = order_obj.search(
                cr, uid, [
                    ('partner_invoice_id', 'in', child_ids + [partner.id]),
                    ('state', 'not in', ['draft', 'sent', 'done', 'cancel']),
                    ('invoice_ids', '=', False)])
            for order in order_obj.browse(cr, uid, order_ids):
                    sale_credit += order.amount_total
                    
            inv_ids = inv_obj.search(cr, uid, 
                        [
                    ('partner_id', 'in', child_ids + [partner.id]),
                    ('state', 'in', ['draft', ])])
            for inv in inv_obj.browse(cr, uid, inv_ids):
                inv_credit += inv.amount_total
            res[partner.id]['sale_credit'] = sale_credit
            res[partner.id]['total_credit'] =\
                sale_credit + res[partner.id].get('credit', 0) + inv_credit
        return res

    _columns = {
        'distribution_costs': fields.float('Distribution costs'),
        'credit_usual': fields.float('Credit usual'),
        'sale_credit': fields.function(
            _compute_credit_info, type='float', multi='credit_info',
            string='Sale Orders Receivable'),
        'total_credit': fields.function(
            _compute_credit_info, type='float', multi='credit_info',
            string='Total Receivable (With Sale Orders)'),
        'after_days': fields.integer(default=30),
        }
        
    def check_after_payment_term(self, cr, uid, ids, context=None):
        ctx = context.copy()
        ctx['all_fiscalyear'] = True
        query = self.pool.get('account.move.line')._query_get(cr, uid, context=ctx)
        cr.execute("""SELECT EXISTS
                      (SELECT l.partner_id, a.type, SUM(l.debit-l.credit)
                      FROM account_move_line l
                      LEFT JOIN account_account a ON (l.account_id=a.id)
                      INNER JOIN res_partner part on (l.partner_id=part.id)
                      WHERE a.type IN ('receivable','payable')
                      AND l.partner_id IN %s
                      AND l.reconcile_id IS NULL
                      AND( l.date_maturity +  part.after_days)<NOW()
                      AND """ + query + """
                      GROUP BY l.partner_id, a.type)
                      """,
                   (tuple(ids),))
        maps = {'receivable':'credit', 'payable':'debit' }
        res = {}
        for val in cr.fetchall():
            if val is None: val=0
            res = val
        return res
