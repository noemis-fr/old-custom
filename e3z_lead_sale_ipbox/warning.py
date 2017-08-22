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
from openerp.osv import fields,osv
from openerp.tools.translate import _
from __builtin__ import isinstance
from dateutil.relativedelta import relativedelta


class sale_order(osv.osv):
    _inherit = 'sale.order'
    def onchange_partner_id(self, cr, uid, ids, part, context=None):
        warning = {}
        title = False
        message = False
        
        result_check = self.check_credit_condition(cr, uid, ids,part,True,context)

        result =  super(sale_order, self).onchange_partner_id(cr, uid, ids, part, context=context)
        
        if result_check.get('warning',False):
            if result.get('warning',False):
                warning['title'] = result_check['warning']['title'] and result_check['warning']['title'] +' & '+ result['warning']['title'] or result['warning']['title']
                warning['message'] = result_check['warning']['message'] and result_check['warning']['message'] + ' ' + result['warning']['message'] or result['warning']['message']
            else:
                warning['title'] = result_check['warning']['title']
                warning['message'] = result_check['warning']['message']
            if warning:
                result['warning'] = warning

        return result
    
    def check_credit_condition(self,cr, uid, ids,part = None,on_change = False, context = None):
        
        users_obj = self.pool.get('res.users')
        text_error = None
        warning = {}
        result = {}
        
        if not isinstance(ids,type([])):
            ids=[ids]
        if(part==None):
            for order in self.pool.get('sale.order').browse(cr, uid, ids, context):
                part=order.partner_invoice_id.id
        
        
        partner = self.pool.get('res.partner').browse(cr, uid, part, context=context)
        
        
        if partner.commercial_partner_id.total_credit > partner.commercial_partner_id.credit_limit and not users_obj.has_group(cr, uid, 'account.group_account_user') and not users_obj.has_group(cr, uid, 'account.group_account_manager'):
            text_error = _('Credit limit allowed is reached.').format(partner.commercial_partner_id.total_credit, partner.commercial_partner_id.credit_limit)
            if partner.commercial_partner_id.credit_limit < partner.commercial_partner_id.credit_usual:
                text_error += _('\nInsurance credit: {},\nComputed Credit: {},\nUsual credit: {}').format( partner.commercial_partner_id.credit_limit, partner.commercial_partner_id.total_credit, partner.commercial_partner_id.credit_usual)
        if partner.commercial_partner_id.check_after_payment_term()==True:
            if text_error == None:
                text_error = _('date limite de paiement + délai dépassée.').format(partner.commercial_partner_id.total_credit, partner.commercial_partner_id.credit_limit)
            else :
                text_error += _('date limite de paiement + délai dépassée.').format(partner.commercial_partner_id.total_credit, partner.commercial_partner_id.credit_limit)
        if text_error !=None:
            if on_change !=True:
                raise osv.except_osv(_('Error!'), text_error)
            warning['title'] = 'problème comptabilité, id du client :'+str(part)
            warning['message'] = text_error
        
        if warning:
            result['warning'] = warning
            
        return result
sale_order()

