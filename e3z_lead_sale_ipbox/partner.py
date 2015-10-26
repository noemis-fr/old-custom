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

    def _credit_debit_get(self, cr, uid, ids, field_names, arg, context=None):
        res = super(res_partner, self)._credit_debit_get(cr, uid, ids, field_names, arg, context)
        order_obj = self.pool.get('sale.order')
        invoice_obj = self.pool.get('account.invoice')
        credit = 0
        for id in ids:
            # Récupération des factures ouvertes
            invoice_ids = invoice_obj.search(cr, uid, ['&', ('partner_id', '=', id), ('state', '=', ['open']), ('type', '=', 'out_invoice')])
            for invoice in invoice_obj.browse(cr, uid, invoice_ids):
                credit += invoice.amount_total

            # Récupération des commandes non facturées
            order_ids = order_obj.search(cr, uid, ['&', ('partner_invoice_id', '=', id), ('state', 'not in', ['draft', 'sent', 'done', 'cancel']), ('invoice_ids', '=', False)])
            for order in order_obj.browse(cr, uid, order_ids):
                    credit += order.amount_total
            
            # Prise en compte des avoirs
            refund_ids = invoice_obj.search(cr, uid, ['&', '&', ('partner_id', '=', id), ('state', '=', 'open'), ('type', '=', 'out_refund')])
            for refund in invoice_obj.browse(cr, uid, refund_ids):
                credit -= refund.amount_total
            
            res[id].update({'credit': credit})
        return res

    def _credit_search(self, cr, uid, obj, name, args, context=None):
        return self._asset_difference_search(cr, uid, obj, name, 'receivable', args, context=context)

    def _debit_search(self, cr, uid, obj, name, args, context=None):
        return self._asset_difference_search(cr, uid, obj, name, 'payable', args, context=context)

    _columns = {
        'credit_usual': fields.float('Credit usual'),
        'credit': fields.function(_credit_debit_get,
            fnct_search=_credit_search, string='Total Receivable', multi='dc', help="Total amount this customer owes you."),
        'debit': fields.function(_credit_debit_get, fnct_search=_debit_search, string='Total Payable', multi='dc', help="Total amount you have to pay to this supplier."),
    }
