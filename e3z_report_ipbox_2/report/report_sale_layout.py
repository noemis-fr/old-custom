##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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
from report import report_sxw
from lxml import etree
from openerp.osv import osv,fields
from openerp.tools.translate import _

rml_parents = {
    'tr': 1,
    'li': 1,
    'story': 0,
    'section': 0
}

class sale_order_1(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(sale_order_1, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'sale_order_lines': self.sale_order_lines,
          #  'repeat_In':self.repeat_In,
        })
        self.context = context

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
    
    def sale_order_lines(self, sale_order):
        result = []
        sub_total = {}
        order_lines = []
        res = {}
        obj_order_line = self.pool.get('sale.order.line')
        ids = obj_order_line.search(self.cr, self.uid, [('order_id', '=', sale_order.id)])
        for id in range(0, len(ids)):
            order = obj_order_line.browse(self.cr, self.uid, ids[id], self.context.copy())
            order_lines.append(order)

        i = 1
        j = 0
        sum_flag = {}
        sum_flag[j] = -1
        for entry in order_lines:
            res = {}

            if entry.layout_type == 'article':
                res['tax_id'] = ', '.join(map(lambda x: x.description, entry.tax_id)) or ''
                res['name'] = entry.name
                res['product_uom_qty'] = entry.product_uom_qty or 0.00
                res['product_uom'] = entry.product_uom and entry.product_uom.name or ''
                res['price_unit'] = entry.puvr or 0.00
                res['discount'] = entry.discount and entry.discount or 0.00
                res['price_subtotal'] = entry.price_subtotal and entry.price_subtotal or 0.00
                sub_total[i] = entry.price_subtotal and entry.price_subtotal
                i = i + 1
                res['note'] = '' #entry.note or ''
                res['currency'] = sale_order.pricelist_id.currency_id.symbol
                res['layout_type'] = entry.layout_type
                res['code'] = entry.product_id.default_code
            else:
                res['product_uom_qty'] = ''
                res['price_unit'] = ''
                res['discount'] = ''
                res['tax_id'] = ''
                res['layout_type'] = entry.layout_type
                res['note'] = '' #entry.note or ''
                res['product_uom'] = ''
                res['code'] = ''

                if entry.layout_type == 'subtotal':
                    res['name'] = entry.name
                    sum = 0
                    sum_id = 0
                    if sum_flag[j] == -1:
                        temp = 1
                    else:
                        temp = sum_flag[j]

                    for sum_id in range(temp, len(sub_total)+1):
                        sum += sub_total[sum_id]
                    sum_flag[j+1] = sum_id +1

                    j = j + 1
                    res['price_subtotal'] = sum
                    res['currency'] = sale_order.pricelist_id.currency_id.name
                    res['quantity'] = ''
                    res['price_unit'] = ''
                    res['discount'] = ''
                    res['tax_id'] = ''
                    res['product_uom'] = ''
                elif entry.layout_type == 'title':
                    res['name'] = entry.name
                    res['price_subtotal'] = ''
                    res['currency'] = ''
                elif entry.layout_type == 'text':
                    res['name'] = entry.name
                    res['price_subtotal'] = ''
                    res['currency'] = ''
                elif entry.layout_type == 'line':
                    res['product_uom_qty'] = '_____'
                    res['price_unit'] = '______________'
                    res['discount'] = '___________'
                    res['tax_id'] = '_______________'
                    res['product_uom'] = '_____'
                    res['name'] = '_______________________________________'
                    res['price_subtotal'] = '_________'
                    res['currency'] = '_______'
                elif entry.layout_type == 'break':
                    res['layout_type'] = entry.layout_type
                    res['name'] = entry.name
                    res['price_subtotal'] = ''
                    res['currency'] = ''
                else:
                    res['name'] = entry.name
                    res['price_subtotal'] = ''
                    res['currency'] = sale_order.pricelist_id.currency_id.name

            result.append(res)
        return result

#report_sxw.report_sxw('report.sale.order.layout2', 'sale.order', 'addons/sale_layout/report/report_sale_layout.rml', parser=sale_order_1,header="header_shipping_sale")
report_sxw.report_sxw(
    'report.sale.order.layout3',
    'sale.order',
    'addons/sale_layout/report/report_sale_layout_proforma.rml',
    parser=sale_order_1)
