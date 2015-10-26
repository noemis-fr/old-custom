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


class sale_order(osv.osv):
    _inherit = 'sale.order'

    def create(self, cr, uid, vals, context=None):
        usr_obj = self.pool.get('res.users')
        group_obj = self.pool.get('res.groups')
        ir_model_data = self.pool.get('ir.model.data')
        adv_group_id = ir_model_data.get_object_reference(cr, uid, 'sale', 'adv')[1]
        adv_users = group_obj.browse(cr, uid, adv_group_id).users
        if not vals.get('message_follower_ids', False):
            vals['message_follower_ids'] = []
        if adv_users:
            for adv_user_id in adv_users:
                adv_id = usr_obj.browse(cr, uid, adv_user_id.id).partner_id.id
                vals['message_follower_ids'] += [4, adv_id]

        mrp_group_id = ir_model_data.get_object_reference(cr, uid, 'mrp', 'team')[1]
        mrp_users = group_obj.browse(cr, uid, mrp_group_id).users
        if mrp_users:
            for mrp_user_id in mrp_users:
                mrp_id = usr_obj.browse(cr, uid, mrp_user_id.id).partner_id.id
                vals['message_follower_ids'] += [4, mrp_id]

        new_id = super(sale_order, self).create(cr, uid, vals, context)

        follower_ids = self.pool.get('mail.followers').search(cr, uid, [('res_id', '=', new_id)])

        for follower_id in follower_ids:
            follower = self.pool.get('mail.followers').browse(cr, uid, follower_id)


        return new_id

    def action_button_confirm(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res = super(sale_order, self).action_button_confirm(cr, uid, ids, context)
        self.pool.get('mail.proxy').send_mail(cr, uid, ids, 'sale.order', 'Sales Order - Send by Email', context)
        return res
