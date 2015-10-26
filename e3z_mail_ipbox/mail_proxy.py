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

import logging
from openerp.osv import osv, fields

_logger = logging.getLogger(__name__)


class mail_proxy(osv.osv):
    _name = 'mail.proxy'

    def send_mail(self, cr, uid, ids, model, template_name, context=None):
        if context is None:
            context = {}
        template_obj = self.pool.get('email.template')
        tmpl = template_obj.search(cr,uid,[('name','=', template_name)])[0]

        wiz_obj = self.pool.get('mail.compose.message')

        fields = ['subject', 'composition_mode', 'attachment_ids', 'parent_id', 'partner_ids', 'body', 'model', 'record_name', 'res_id', 'template_id']
        context.update({'active_model': model, 'active_ids': ids, 'default_composition_mode': 'comment', 'default_model': model, 'lang': 'fr_FR'})
        values = wiz_obj.default_get(cr, uid, fields, context)
        email = wiz_obj.generate_email_for_composer(cr, uid, tmpl, ids[0], context)
        attachment = email.get('attachments', False)
        attach_fname = attachment[0][0]
        attach_datas = attachment[0][1]
        data_attach = {
                    'name': attach_fname,
                    'datas': attach_datas,
                    'datas_fname': attach_fname,
                    'res_model': model,
                    'res_id': ids[0],
                    'type': 'binary',  # override default_type from context, possibly meant for another model!
                }
        attach_id = self.pool.get('ir.attachment').search(cr, uid, [('res_model', '=', model), ('res_id', 'in', ids)])
        if not attach_id:
            attach_id = self.pool.get('ir.attachment').create(cr, uid, data_attach, context=context)
        values.update(email)

        if type(attach_id) == list:
            values['attachment_ids'] = [(4, attach_id[0])]
        else:
            values['attachment_ids'] = [(4, attach_id)]
        values['template_id'] = tmpl
        values['res_id'] = ids[0]
        # values['partner_ids'] = [partner.id for partner in self.pool.get(model).browse(cr, uid, ids[0]).message_follower_ids]
        wiz_id = wiz_obj.create(cr, uid, values, context)
        wizard = wiz_obj.browse(cr, uid, wiz_id, context)
        wiz_obj.send_mail(cr, uid, [wiz_id], context)
        # active_ids = context.get('active_ids')
        # is_log = context.get('mail_compose_log', False)
        #
        # active_model_pool_name = wizard.model if wizard.model else 'mail.thread'
        # active_model_pool = self.pool.get(active_model_pool_name)
        #
        # # wizard works in batch mode: [res_id] or active_ids
        # res_ids = active_ids
        # for res_id in res_ids:
        #     # mail.message values, according to the wizard options
        #     post_values = {
        #         'subject': wizard.subject,
        #         'body': wizard.body,
        #         'parent_id': wizard.parent_id and wizard.parent_id.id,
        #         'partner_ids': [partner.id for partner in wizard.partner_ids],
        #         'attachment_ids': [attach.id for attach in wizard.attachment_ids],
        #     }
        #     # post the message
        #     subtype = 'mail.mt_comment'
        #     if is_log:  # log a note: subtype is False
        #         subtype = False
        #     msg_id = active_model_pool.message_post(cr, uid, [res_id], type='comment', subtype=subtype, context=context, **post_values)
        return True
