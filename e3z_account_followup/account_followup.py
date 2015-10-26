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

from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import datetime

class followup_line(osv.osv):

    _inherit = 'account_followup.followup.line'

    _columns = {
        'description2': fields.text('Printed Message 2', translate=True),
    }


class res_partner(osv.osv):
    _inherit = "res.partner"

    def do_button_print(self, cr, uid, ids, context=None):
        assert(len(ids) == 1)
        company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        #search if the partner has accounting entries to print. If not, it may not be present in the
        #psql view the report is based on, so we need to stop the user here.

        max_date = datetime.now().date().strftime('%Y-%m-%d')

        if not self.pool.get('account.move.line').search(cr, uid, [
                                                                   ('partner_id', '=', ids[0]),
                                                                   ('account_id.type', '=', 'receivable'),
                                                                   ('reconcile_id', '=', False),
                                                                   ('state', '!=', 'draft'),
                                                                   ('company_id', '=', company_id),
                                                                   ('date_maturity', '<', max_date)
                                                                  ], context=context):
            raise osv.except_osv(_('Error!'),_("The partner does not have any accounting entries to print in the overdue report for the current company."))
        self.message_post(cr, uid, [ids[0]], body=_('Printed overdue payments report'), context=context)
        #build the id of this partner in the psql view. Could be replaced by a search with [('company_id', '=', company_id),('partner_id', '=', ids[0])]
        wizard_partner_ids = [ids[0] * 10000 + company_id]
        followup_ids = self.pool.get('account_followup.followup').search(cr, uid, [('company_id', '=', company_id)], context=context)
        if not followup_ids:
            raise osv.except_osv(_('Error!'),_("There is no followup plan defined for the current company."))
        data = {
            'date': fields.date.today(),
            'followup_id': followup_ids[0],
        }
        #call the print overdue report on this partner
        return self.do_partner_print(cr, uid, wizard_partner_ids, data, context=context)