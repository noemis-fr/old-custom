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
from openerp import tools
from openerp import SUPERUSER_ID


class crm_lead(osv.osv):
    _inherit = 'crm.lead'

    _columns = {
        'sale_id': fields.many2one('sale.order', 'Order'),
    }

    def message_post(self, cr, uid, thread_id, body='', subject=None, type='notification',
                        subtype=None, parent_id=False, attachments=None, context=None,
                        content_subtype='html', **kwargs):
        res = super(crm_lead, self).message_post(cr, uid, thread_id, body, subject, type, subtype, parent_id, attachments, context, content_subtype)

        mail_message = self.pool.get('mail.message')
        ir_attachment = self.pool.get('ir.attachment')

        email_from = kwargs.get('email_from')
        if email_from and thread_id and type == 'email' and kwargs.get('author_id'):
            email_list = tools.email_split(email_from)
            doc = self.browse(cr, uid, thread_id, context=context)
            if email_list and doc:
                author_ids = self.pool.get('res.partner').search(cr, uid, [
                                        ('email', 'ilike', email_list[0]),
                                        ('id', 'in', [f.id for f in doc.message_follower_ids])
                                    ], limit=1, context=context)
                if author_ids:
                    kwargs['author_id'] = author_ids[0]
        author_id = kwargs.get('author_id')
        if author_id is None:  # keep False values
            author_id = self.pool.get('mail.message')._get_default_author(cr, uid, context=context)

        model = False
        if thread_id:
            model = context.get('thread_model', self._name) if self._name == 'mail.thread' else self._name
            if model != self._name:
                del context['thread_model']
                return self.pool.get(model).message_post(cr, uid, thread_id, body=body, subject=subject, type=type, subtype=subtype, parent_id=parent_id, attachments=attachments, context=context, content_subtype=content_subtype, **kwargs)

        partner_ids = set()
        kwargs_partner_ids = kwargs.pop('partner_ids', [])
        for partner_id in kwargs_partner_ids:
            if isinstance(partner_id, (list, tuple)) and partner_id[0] == 4 and len(partner_id) == 2:
                partner_ids.add(partner_id[1])
            if isinstance(partner_id, (list, tuple)) and partner_id[0] == 6 and len(partner_id) == 3:
                partner_ids |= set(partner_id[2])
            elif isinstance(partner_id, (int, long)):
                partner_ids.add(partner_id)
            else:
                pass  # we do not manage anything else
        if parent_id and not model:
            parent_message = mail_message.browse(cr, uid, parent_id, context=context)
            private_followers = set([partner.id for partner in parent_message.partner_ids])
            if parent_message.author_id:
                private_followers.add(parent_message.author_id.id)
            private_followers -= set([author_id])
            partner_ids |= private_followers

        attachment_ids = kwargs.pop('attachment_ids', []) or []  # because we could receive None (some old code sends None)
        if attachment_ids:
            filtered_attachment_ids = ir_attachment.search(cr, SUPERUSER_ID, [
                ('res_model', '=', 'mail.compose.message'),
                ('create_uid', '=', uid),
                ('id', 'in', attachment_ids)], context=context)
            if filtered_attachment_ids:
                ir_attachment.write(cr, SUPERUSER_ID, filtered_attachment_ids, {'res_model': model, 'res_id': thread_id}, context=context)
        attachment_ids = [(4, id) for id in attachment_ids]

        subtype_id = False
        if subtype:
            if '.' not in subtype:
                subtype = 'mail.%s' % subtype
            ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, *subtype.split('.'))
            subtype_id = ref and ref[1] or False

        if model == 'crm.lead':
            model = 'sale.order'
            lead= self.pool.get('crm.lead').browse(cr, uid, thread_id)
            if isinstance(lead, list):
                lead = lead[0]
            thread_id = lead.user_id.id
            

        values = kwargs
        values.update({
            'author_id': author_id,
            'model': model,
            'res_id': thread_id or False,
            'body': body,
            'subject': subject or False,
            'type': type,
            'parent_id': parent_id,
            'attachment_ids': attachment_ids,
            'subtype_id': subtype_id,
            'partner_ids': [(4, pid) for pid in partner_ids],
        })

        # Avoid warnings about non-existing fields
        for x in ('from', 'to', 'cc'):
            values.pop(x, None)

        # Create and auto subscribe the author
        if thread_id:
            msg_id = mail_message.create(cr, uid, values, context=context)
        return res
    