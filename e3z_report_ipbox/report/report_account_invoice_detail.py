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

from report import report_sxw
from lxml import etree
from openerp.osv import osv,fields
from openerp.tools.translate import _

class account_invoice_detail(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(account_invoice_detail, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'invoice_lines': self.invoice_lines,
            'get_shipping_address': self._get_shipping_address,
        })
        self.context = context
        self._node = None
        
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
    
    def _get_shipping_address(self, invoice):
        shipping_name = ''
        shipping_address = ''
        self.cr.execute('select order_id from sale_order_invoice_rel where invoice_id=%s', (invoice.id,))
        ids = map(lambda x: x[0], self.cr.fetchall())
#         ids = self.pool.get('sale.order').search(self.cr, self.uid, [('invoice_ids', 'child_of', invoice.id)])
        if ids and len(ids) == 1:
            order = self.pool.get('sale.order').browse(self.cr, self.uid, ids[0], self.context.copy())
            shipping_name = ((order.partner_shipping_id and order.partner_id.title and order.partner_shipping_id.title.name) or '') + ' ' + ((order.partner_shipping_id and order.partner_shipping_id.name) or '')
            shipping_address = order.partner_shipping_id and self.display_address(order.partner_shipping_id)
        else:
            ids = self.pool.get('stock.picking.out').search(self.cr, self.uid, [('name', 'in', invoice.origin.split(':'))])
            if ids and len(ids) == 1:
                picking = self.pool.get('stock.picking.out').browse(self.cr, self.uid, ids[0], self.context.copy())
                shipping_name = ((picking.partner_shipping_id and picking.partner_id.title and picking.partner_shipping_id.title.name) or '') + ' ' + ((picking.partner_shipping_id and order.partner_shipping_id.name) or '')
                shipping_address = picking.partner_shipping_id and self.display_address(picking.partner_shipping_id)
        return shipping_name + '\n' + shipping_address

    def invoice_lines(self, invoice):
        result = []
        sub_total = {}
        info = []
        res = {}
        list_in_seq = {}
        ids = self.pool.get('account.invoice.line').search(self.cr, self.uid, [('invoice_id', '=', invoice.id)])
        ids.sort()
        invoice_list = []
        for id in range(0, len(ids)):
            info = self.pool.get('account.invoice.line').browse(self.cr, self.uid, ids[id], self.context.copy())
            invoice_list.append(info)

        for invoice_browse in invoice_list:
            list_in_seq[invoice_browse] = invoice_browse.sequence
        i = 1
        j = 0
        final=sorted(list_in_seq.items(), lambda x, y: cmp(x[1], y[1]))
        invoice_list = [x[0] for x in final]


        sum_flag = {}
        sum_flag[j] = -1
        for entry in invoice_list:
            res = {}
            self.cr.execute('select tax_id from account_invoice_line_tax where invoice_line_id=%s', (entry.id,))
            tax_ids = self.cr.fetchall()
            if tax_ids == []:
                res['tax_types'] = ''
            else:
                tax_names_dict = {}
                for item in range(0, len(tax_ids)):
                    self.cr.execute('select name from account_tax where id=%s', (tax_ids[item][0],))
                    type = self.cr.fetchone()
                    tax_names_dict[item] = type[0]
                tax_names = ','.join([tax_names_dict[x] for x in range(0, len(tax_names_dict))])
                res['tax_types'] = tax_names
            res['name'] = entry.name
            res['default_code'] = entry.product_id.default_code
            res['quantity'] = self.formatLang(entry.quantity, digits=self.get_digits(dp='Account'))
            res['price_unit'] = self.formatLang(entry.price_unit, digits=self.get_digits(dp='Account'))
            res['discount'] = self.formatLang(entry.discount, digits=self.get_digits(dp='Account'))
            res['price_subtotal'] = self.formatLang(entry.price_subtotal, digits=self.get_digits(dp='Account'))
            sub_total[i] = entry.price_subtotal
            i = i + 1
            res['note'] = '' #entry.note
            res['currency'] = invoice.currency_id.symbol
            res['type'] = 'article'
            if entry.uos_id.id == False:
                res['uos'] = ''
            else:
                uos_name = self.pool.get('product.uom').read(self.cr, self.uid, entry.uos_id.id, ['name'], self.context.copy())
                res['uos'] = uos_name['name']

            result.append(res)
        return result

report_sxw.report_sxw('report.account.invoice.detail', 'account.invoice', 'addons/e3z_report_ipbox/report/report_account_invoice.rml', parser=account_invoice_detail,header="header_invoice")
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

