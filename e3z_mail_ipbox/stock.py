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
from openerp import netsvc


class stock_picking(osv.osv):
    _inherit = 'stock.picking'

    def create(self, cr, uid, vals, context=None):
        usr_obj = self.pool.get('res.users')
        group_obj = self.pool.get('res.groups')
        ir_model_data = self.pool.get('ir.model.data')
        adv_group_id = ir_model_data.get_object_reference(cr, uid, 'sale', 'adv')[1]
        adv_users = group_obj.browse(cr, uid, adv_group_id).users
        if vals.get('message_follower_ids', False):
            if adv_users:
                for adv_user_id in adv_users:
                    adv_id = usr_obj.browse(cr, uid, adv_user_id.id).partner_id.id
                    vals['message_follower_ids'] = [4, adv_id]


            mrp_group_id = ir_model_data.get_object_reference(cr, uid, 'mrp', 'team')[1]
            mrp_users = group_obj.browse(cr, uid, mrp_group_id).users
            if mrp_users:
                for mrp_user_id in mrp_users:
                    mrp_id = usr_obj.browse(cr, uid, mrp_user_id.id).partner_id.id
                    vals['message_follower_ids'] += [4, mrp_id]


            acc_group_id = ir_model_data.get_object_reference(cr, uid, 'account', 'group_account_manager')[1]
            acc_users = group_obj.browse(cr, uid, acc_group_id).users
            if mrp_users:
                for acc_user_id in acc_users:
                    acc_id = usr_obj.browse(cr, uid, acc_user_id.id).partner_id.id
                    vals['message_follower_ids'] += [4, acc_id]
        return super(stock_picking, self).create(cr, uid, vals, context)

    def action_done(self, cr, uid, ids, context=None):
        """Changes picking state to done.

        This method is called at the end of the workflow by the activity "done".
        @return: True
        """
        if not context:
            context = {}
        super(stock_picking, self).action_done(cr, uid, ids, context)

        for id in ids:
            picking = self.browse(cr, uid, id)

        if picking.type == 'out':
            self.pool.get('mail.proxy').send_mail(cr, uid, ids, 'stock.picking.out', 'Stock Picking - Send by Email', context)
        return True

class stock_picking_out(osv.osv):
    _inherit = 'stock.picking.out'

    def action_quotation_send(self, cr, uid, ids, context=None):
        '''
        This function opens a window to compose an email, with the edi stock template message loaded by default
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        ir_model_data = self.pool.get('ir.model.data')
        try:
            template_id = ir_model_data.get_object_reference(cr, uid, 'stock', 'email_template_edi_stock')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(context)
        ctx.update({
            'default_model': 'stock.picking.out',
            'default_res_id': ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }


# class stock_picking(osv.osv):
#     _inherit = 'stock.picking'
#
#     def action_done(self, cr, uid, ids, context=None):
#         """Changes picking state to done.
#
#         This method is called at the end of the workflow by the activity "done".
#         @return: True
#         """
#         if not context:
#             context = {}
#         super(stock_picking, self).action_done(cr, uid, ids, context)
#
#         self.pool.get('mail.proxy').send_mail(cr, uid, ids, 'stock.picking.out', 'Stock Picking - Send by Email', context)
#         return True