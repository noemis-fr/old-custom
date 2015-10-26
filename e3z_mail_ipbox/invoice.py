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



class account_invoice(osv.osv):
    _inherit = 'account.invoice'

    def create(self, cr, uid, vals, context=None):
        if vals.get('origin', False):
            sale_ids = self.pool.get('sale.order').search(cr, uid, [('name', '=', vals['origin'])])
            if not sale_ids:
                origin = vals['origin'].split(':')
                sale_ids = self.pool.get('sale.order').search(cr, uid, [('name', 'in', origin)])

            if sale_ids:
                for sale_id in sale_ids:
                    sale = self.pool.get('sale.order').browse(cr, uid, sale_id)
                    com_id = sale.user_id.partner_id.id
                    vals['message_follower_ids'] = [4, com_id]

        return super(account_invoice, self).create(cr, uid, vals, context)

    def invoice_validate(self, cr, uid, ids, context=None):
        super(account_invoice, self).invoice_validate(cr, uid, ids, context)
        if context is None:
            context = {'lang': 'fr_FR'}
        self.pool.get('mail.proxy').send_mail(cr, uid, ids, 'account.invoice', 'Invoice - Send by Email', context)
        return True