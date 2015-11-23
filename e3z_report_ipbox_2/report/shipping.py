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

from openerp.report import report_sxw
from lxml import etree
from openerp.osv import osv,fields
from openerp.tools.translate import _

class shipping(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(shipping, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_product_desc': self.get_product_desc
        })
        
    def _add_header(self, rml_dom,header='external'):
        in_rml_header = False
        if header=='internal':
            rml_head =  self.rml_header2
        elif header=='internal landscape':
            rml_head =  self.rml_header3
        elif header=='external':
            rml_head =  self.rml_header
        elif not header:
            in_rml_header= True
        else:
            header_obj= self.pool.get('res.header')
            rml_head_id = header_obj.search(self.cr,self.uid,[('name','=',header)])
            if rml_head_id:
                rml_head = header_obj.browse(self.cr, self.uid, rml_head_id[0]).rml_header
        if not in_rml_header:
            try:
                head_dom = etree.XML(rml_head)
            except:
                raise osv.except_osv(_('Error in report header''s name !'), _('No proper report''s header defined for the selected report. Check that the report header defined in your report rml_parse line exist in Administration/reporting/Reporting headers.' ))

        if not in_rml_header:
            for tag in head_dom:
                found = rml_dom.find('.//'+tag.tag)
                if found is not None and len(found):
                    if tag.get('position'):
                        found.append(tag)
                    else :
                        found.getparent().replace(found,tag)
        else:
            head_dom = etree.XML(etree.tostring(rml_dom.find('.//pageTemplate')))
            for tag in head_dom:
                found = rml_dom.find('.//'+tag.tag)
                if found is not None and len(found):
                    if tag.get('position'):
                        found.append(tag)
                    else :
                        found.getparent().replace(found,tag)
        return True
    
    def get_product_desc(self, move_line):
        desc = move_line.product_id.name
        if move_line.product_id.default_code:
            desc = '[' + move_line.product_id.default_code + ']' + ' ' + desc
        return desc

#report_sxw.report_sxw('report.sale.shipping1','stock.picking','addons/e3z_report_ipbox_2/report/shipping.rml',parser=shipping,header="header_shipping_sale")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
