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
from urllib import urlencode
from urlparse import urljoin
from openerp.osv.orm import except_orm
from openerp.tools.translate import _
from openerp import tools

from openerp.addons.portal import mail_mail


def send_get_mail_body2(self, cr, uid, mail, partner=None, context=None):
    """ Return a specific ir_email body. The main purpose of this method
        is to be inherited by Portal, to add a link for signing in, in
        each notification email a partner receives.

        :param browse_record mail: mail.mail browse_record
        :param browse_record partner: specific recipient partner
    """
    body = mail.body_html
    # partner is a user, link to a related document (incentive to install portal)
    if partner and partner.user_ids and mail.model and mail.res_id \
            and self.check_access_rights(cr, partner.user_ids[0].id, 'read', raise_exception=False):
        related_user = partner.user_ids[0]
        try:
            self.pool.get(mail.model).check_access_rule(cr, related_user.id, [mail.res_id], 'read', context=context)
            base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
            # the parameters to encode for the query and fragment part of url
            query = {'db': cr.dbname}
            fragment = {
                'login': related_user.login,
                'model': mail.model,
                'id': mail.res_id,
            }
        except except_orm, e:
            pass
    return body

mail_mail.mail_mail.send_get_mail_body = send_get_mail_body2