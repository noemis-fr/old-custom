# -*- coding: utf-8 -*-
##############################################################################
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
##############################################################################

from openerp.osv import osv, orm, fields

class mail_message(osv.Model):

    _inherit = 'mail.message'

    def _get_partner_id(self, cr, uid, ids, name, arg, context=None):
        """ Compute if the message is unread by the current user. """
        res = dict((id, False) for id in ids)
        for mail in self.browse(cr, uid, ids, context):
            if mail.model == 'res.partner':
                res[mail.id] = mail.res_id
        return res

    _columns = {
        'partner_id': fields.function(_get_partner_id, type='many2one', string='Partner', relation='res.partner'),
    }