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

import time
from collections import defaultdict

from openerp import pooler
from openerp.report import report_sxw
from openerp.addons.account_followup.report.account_followup_print import report_rappel

class report_rappel(report_rappel):
    
    def __init__(self, cr, uid, name, context=None):
        super(report_rappel, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_text2': self._get_text2,
            'get_title': self._get_title
        })
        
    def _get_title(self, stat_line, followup_id, context=None):
        if context is None:
            context = {}
        context.update({'lang': stat_line.partner_id.lang})
        fp_obj = pooler.get_pool(self.cr.dbname).get('account_followup.followup')
        fp_line = fp_obj.browse(self.cr, self.uid, followup_id, context=context).followup_line
        if not fp_line:
            raise osv.except_osv(_('Error!'), _("The followup plan defined for the current company does not have any followup action."))
        # the default text will be the first fp_line in the sequence with a description2.
        default_title = ''
        li_delay = []
        for line in fp_line:
            if not default_title and line.name:
                default_title = line.name
            li_delay.append(line.delay)
        li_delay.sort(reverse=True)
        a = {}
                # look into the lines of the partner that already have a followup level, and take the title of the higher level for which it is available
        partner_line_ids = pooler.get_pool(self.cr.dbname).get('account.move.line').search(self.cr, self.uid, [('partner_id', '=', stat_line.partner_id.id), ('reconcile_id', '=', False), ('company_id', '=', stat_line.company_id.id), ('blocked', '=', False), ('state', '!=', 'draft'), ('debit', '!=', False), ('account_id.type', '=', 'receivable'), ('followup_line_id', '!=', False)])
        partner_max_delay = 0
        partner_max_title = ''
        for i in pooler.get_pool(self.cr.dbname).get('account.move.line').browse(self.cr, self.uid, partner_line_ids, context=context):
            if i.followup_line_id.delay > partner_max_delay and i.followup_line_id.name:
                partner_max_delay = i.followup_line_id.delay
                partner_max_title = i.followup_line_id.name
        title = partner_max_delay and partner_max_title or default_title
        
        return title

    def _get_text2(self, stat_line, followup_id, context=None):
        if context is None:
            context = {}
        context.update({'lang': stat_line.partner_id.lang})
        fp_obj = pooler.get_pool(self.cr.dbname).get('account_followup.followup')
        fp_line = fp_obj.browse(self.cr, self.uid, followup_id, context=context).followup_line
        if not fp_line:
            raise osv.except_osv(_('Error!'), _("The followup plan defined for the current company does not have any followup action."))
        # the default text will be the first fp_line in the sequence with a description2.
        default_text = ''
        li_delay = []
        for line in fp_line:
            if not default_text and line.description2:
                default_text = line.description2
            li_delay.append(line.delay)
        li_delay.sort(reverse=True)
        a = {}
        # look into the lines of the partner that already have a followup level, and take the description2 of the higher level for which it is available
        partner_line_ids = pooler.get_pool(self.cr.dbname).get('account.move.line').search(self.cr, self.uid, [('partner_id', '=', stat_line.partner_id.id), ('reconcile_id', '=', False), ('company_id', '=', stat_line.company_id.id), ('blocked', '=', False), ('state', '!=', 'draft'), ('debit', '!=', False), ('account_id.type', '=', 'receivable'), ('followup_line_id', '!=', False)])
        partner_max_delay = 0
        partner_max_text = ''
        for i in pooler.get_pool(self.cr.dbname).get('account.move.line').browse(self.cr, self.uid, partner_line_ids, context=context):
            if i.followup_line_id.delay > partner_max_delay and i.followup_line_id.description2:
                partner_max_delay = i.followup_line_id.delay
                partner_max_text = i.followup_line_id.description2
        text = partner_max_delay and partner_max_text or default_text
        if text:
            text = text % {
                'partner_name': stat_line.partner_id.name,
                'date': time.strftime('%Y-%m-%d'),
                'company_name': stat_line.company_id.name,
                'user_signature': pooler.get_pool(self.cr.dbname).get('res.users').browse(self.cr, self.uid, self.uid, context).signature or '',
            }
        return text


report_sxw.report_sxw('report.account_followup.followup.print2',
        'account_followup.stat.by.partner', 'addons/e3z_account_followup/report/account_followup_print.rml',
        parser=report_rappel)
