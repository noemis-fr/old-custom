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
from openerp import SUPERUSER_ID

import logging
_logger = logging.getLogger(__name__)

class mail_thread(osv.osv):
    _inherit = 'mail.thread'


    def create(self, cr, uid, values, context=None):
        """ Chatter override :
            - subscribe uid
            - subscribe followers of parent
            - log a creation message
        """
        if context is None:
            context = {}

        # subscribe uid unless asked not to
        if not context.get('mail_create_nosubscribe'):
            pid = self.pool['res.users'].browse(cr, SUPERUSER_ID, uid).partner_id.id
            message_follower_ids = values.get('message_follower_ids') or []  # webclient can send None or False
            message_follower_ids.append([4, pid])
            values['message_follower_ids'] = message_follower_ids
            # add operation to ignore access rule checking for subscription
            context_operation = dict(context, operation='create')
        else:
            context_operation = context
        _logger.debug("MAIL THREAD FROM e3z")
        thread_id = super(mail_thread, self).create(cr, uid, values, context=context_operation)

        return thread_id