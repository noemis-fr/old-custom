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


class sale_reminder_lead(osv.TransientModel):
    _name = 'sale.reminder.lead'
    _columns = {

    }

    def create_order(self, cr, uid, ids, context=None):
        context.update({'confirm_create': True})
        return self.pool.get('sale.order').create(cr, uid, context.get('vals', {}), context)

    def create_confirm(self, cr, uid, ids, context=None):
        order_obj = self.pool.get('sale.order')
        lead_obj = self.pool.get('crm.lead')
        res = self.pool.get('sale.order').create(cr, uid, context.get('vals', {}), context)
        order = order_obj.browse(cr, uid, res, context)
        if not order.lead_name:
            raise osv.except_osv(_('Error!'), _('There is no lead name, please set one before create the opportunity!'))
        if not order.lead_id:
            lead_id = lead_obj.create(cr, uid, {'name': order.lead_name, 'planned_revenue': order.amount_total,
                                                'type': 'opportunity', 'partner_id': order.partner_id.id,
                                                'sale_id': order.id})
            order.write({'lead_id': lead_id})
        context.update({'confirm_create': True})
        return res