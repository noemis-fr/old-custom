# -*- coding: utf-8 -*-
# OpenERP, Open Source Management Solution
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
from openerp.addons.delivery.stock import stock_picking
from openerp import SUPERUSER_ID


def action_invoice_create2(self, cr, uid, ids, journal_id=False,
        group=False, type='out_invoice', context=None):
    module_is_installed = self.pool.get('ir.module.module').search(cr, SUPERUSER_ID, [('name', '=', 'e3z_add_delivery_method')])
    if module_is_installed:
        module_is_installed = self.pool.get('ir.module.module').read(cr, SUPERUSER_ID, module_is_installed[0], ['state'])
        module_is_installed = module_is_installed.get('state', 'uninstalled') == 'installed' and True or False
    else:
        module_is_installed = False

    # Traitement si le module est installé
    if module_is_installed:
        invoice_obj = self.pool.get('account.invoice')
        picking_obj = self.pool.get('stock.picking')
        invoice_line_obj = self.pool.get('account.invoice.line')
        result = super(stock_picking, self).action_invoice_create(cr, uid,
                ids, journal_id=journal_id, group=group, type=type,
                context=context)
        for picking in picking_obj.browse(cr, uid, result.keys(), context=context):
            if picking.sale_id and len(picking.sale_id.invoice_ids) < 2:
                invoice = invoice_obj.browse(cr, uid, result[picking.id], context=context)
                invoice_line = self._prepare_shipping_invoice_line(cr, uid, picking, invoice, context=context)
                if invoice_line:
                    invoice_line_obj.create(cr, uid, invoice_line)
                    invoice_obj.button_compute(cr, uid, [invoice.id], context=context)
        return result
    # Traitement par défaut, si le module n'est pas installé
    else:
        invoice_obj = self.pool.get('account.invoice')
        picking_obj = self.pool.get('stock.picking')
        invoice_line_obj = self.pool.get('account.invoice.line')
        result = super(stock_picking, self).action_invoice_create(cr, uid,
                ids, journal_id=journal_id, group=group, type=type,
                context=context)
        for picking in picking_obj.browse(cr, uid, result.keys(), context=context):
            invoice = invoice_obj.browse(cr, uid, result[picking.id], context=context)
            invoice_line = self._prepare_shipping_invoice_line(cr, uid, picking, invoice, context=context)
            if invoice_line:
                invoice_line_obj.create(cr, uid, invoice_line)
                invoice_obj.button_compute(cr, uid, [invoice.id], context=context)
        return result

stock_picking.action_invoice_create = action_invoice_create2