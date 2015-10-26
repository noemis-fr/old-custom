# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import pooler
from openerp.report import report_sxw
from openerp.addons.account_followup.report.account_followup_print import report_rappel
from openerp.addons.account_followup.account_followup import res_partner
from datetime import datetime

def _lines_get_with_partner2(self, partner, company_id):
    pool = pooler.get_pool(self.cr.dbname)

    max_date = datetime.now().date().strftime('%Y-%m-%d')

    moveline_obj = pool.get('account.move.line')
    moveline_ids = moveline_obj.search(self.cr, self.uid, [
                        ('partner_id', '=', partner.id),
                        ('account_id.type', '=', 'receivable'),
                        ('reconcile_id', '=', False),
                        ('state', '!=', 'draft'),
                        ('company_id', '=', company_id),
                        ('date_maturity', '<', max_date)
                    ])

    # lines_per_currency = {currency: [line data, ...], ...}
    lines_per_currency = defaultdict(list)
    for line in moveline_obj.browse(self.cr, self.uid, moveline_ids):
        if not line.blocked:
            currency = line.currency_id or line.company_id.currency_id
            line_data = {
                'name': line.move_id.name,
                'ref': line.ref,
                'date': line.date,
                'date_maturity': line.date_maturity,
                'balance': line.amount_currency if currency != line.company_id.currency_id else line.debit - line.credit,
                'debit': line.debit,
                'credit': line.credit,
                'blocked': line.blocked,
                'currency_id': currency,
            }
            lines_per_currency[currency].append(line_data)

    return [{'line': lines} for lines in lines_per_currency.values()]


report_rappel._lines_get_with_partner = _lines_get_with_partner2

def get_followup_table_html2(self, cr, uid, ids, context=None):
    """ Build the html tables to be included in emails send to partners,
        when reminding them their overdue invoices.
        :param ids: [id] of the partner for whom we are building the tables
        :rtype: string
    """
    from openerp.addons.account_followup.report import account_followup_print

    assert len(ids) == 1
    if context is None:
        context = {}
    partner = self.browse(cr, uid, ids[0], context=context)
    # copy the context to not change global context. Overwrite it because _() looks for the lang in local variable 'context'.
    # Set the language to use = the partner language
    context = dict(context, lang=partner.lang)
    followup_table = ''
    if partner.unreconciled_aml_ids:
        company = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id
        current_date = fields.date.context_today(self, cr, uid, context=context)
        rml_parse = account_followup_print.report_rappel(cr, uid, "followup_rml_parser")
        final_res = rml_parse._lines_get_with_partner(partner, company.id)

        for currency_dict in final_res:
            currency = currency_dict.get('line', [{'currency_id': company.currency_id}])[0]['currency_id']
            followup_table += '''
            <table width="100%" cellspacing="0">
            <thead>
            <tr>
                <td style="border: 1px solid black;"><b>''' + _("Reference") + '''</b></td>
                <td style="border: 1px solid black;"><b>''' + _("Due Date") + '''</b></td>
                <td style="border: 1px solid black;"><b>''' + _("Debit") + " (%s)" % (currency.symbol) + '''</b></td>
                <td style="border: 1px solid black;"><b>''' + _("Credit") + " (%s)" % (currency.symbol) + '''</b></td>
            </tr>
            </thead>
            ''' 
            total_balance = 0
            total_debit = 0
            total_credit = 0
            for aml in currency_dict['line']:
                block = aml['blocked'] and 'X' or ' '
                total_balance += aml['balance']
                total_debit += aml['debit']
                total_credit += aml['credit']
                strbegin = "<TD style=\"border: 1px solid black;\">"
                strbeginbold = "<TD style=\"border: 1px solid black;\"><b>"
                strbeginright = "<TD style=\"text-align: right; border: 1px solid black;\">"
                strbeginrightbold = "<TD style=\"text-align: right; border: 1px solid black;\"><b>"
                strend = "</TD>"
                strendbold = "</b></TD>"
                date = aml['date_maturity'] or aml['date']
                followup_table += "<TR>" + strbegin + aml['name'] + strend + strbegin + str(datetime.strptime(date, "%Y-%m-%d").strftime("%d/%m/%Y")) + strend + strbeginright + str(aml['debit'] != 0 and rml_parse.formatLang(aml['debit'], dp='Account') or '&nbsp;') + strend + strbeginright + str(aml['credit'] != 0 and rml_parse.formatLang(aml['credit'], dp='Account') or '&nbsp;') + strend + "</TR>"
            total_balance_str = rml_parse.formatLang((total_balance > 0 and total_balance or -total_balance), dp='Account')
            total_debit_str = rml_parse.formatLang(total_debit, dp='Account')
            total_credit_str = rml_parse.formatLang(total_credit, dp='Account')
            
            followup_table += '<tfoot>'
            followup_table += '<tr>' + "<TD style=\"border: none;\"></TD>" + strbeginbold + _('Total movements') + strendbold + strbeginrightbold + (total_debit != 0 and total_debit_str or '&nbsp;') + strendbold + strbeginrightbold + (total_credit != 0 and total_credit_str or '&nbsp;') + strendbold + '</tr>'
            followup_table += '<tr>' + "<TD style=\"border: none;\"></TD>" + strbeginbold + _('Balance') + strendbold + strbeginrightbold + (total_balance > 0 and total_balance_str or '&nbsp;') + strendbold + strbeginrightbold + (total_balance < 0 and total_balance_str or '&nbsp;') + strendbold + '</tr>'
            followup_table += '</tfoot>'
            followup_table += "</table>"
    return followup_table

res_partner.get_followup_table_html = get_followup_table_html2

def do_partner_print2(self, cr, uid, wizard_partner_ids, data, context=None):
    # wizard_partner_ids are ids from special view, not from res.partner
    if not wizard_partner_ids:
        return {}
    data['partner_ids'] = wizard_partner_ids
    datas = {
         'ids': [],
         'model': 'account_followup.followup',
         'form': data
    }
    return {
        'type': 'ir.actions.report.xml',
        'report_name': 'account_followup.followup.print2',
        'datas': datas,
        }

res_partner.do_partner_print = do_partner_print2

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
