# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-Present Elico Corp. All Rights Reserved.
#    Author:            Eric CAUDAL <contact@elico-corp.com>
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

from osv import fields, osv
from openerp.report import report_sxw
from openerp.tools.translate import _
from lxml import etree
import report

class res_header(osv.osv):
    _name    = "res.header"
    _description = "Reporting headers"
    _columns = {
        'name': fields.char
            ( 
            'Header''s Name', 
            size=128, 
            required=True, 
            help="Header's Name (except 'internal', 'internal landscape' and 'external')"
            ),
        'rml_header': fields.text
            ( 
            'Header''s content', 
            required=True, 
            help="RML header's content"
            ),
        'internal': fields.boolean
            ( 
            'Internal', 
            required=True, 
            help="Header for internal use only"
            ),
    }
    _defaults = {
        'internal':   lambda *a: False,
    }

    def write(self, cr, uid, ids, vals, context=None):
        if vals.get('rml_header', False):
            try:
                head_dom = etree.XML(vals.get('rml_header', False))
            except:
                raise osv.except_osv(_('Error in report header !'), _('Report is not well formated' ))

        return super(res_header, self).write(cr, uid, ids, vals, context=context)

    def create(self, cr, uid, vals, context=None):
        if vals.get('rml_header', False):
            try:
                head_dom = etree.XML(vals.get('rml_header', False))
            except:
                raise osv.except_osv(_('Error in report header !'), _('Report is not well formated' ))
        return super(res_header, self).create(cr, uid, vals, context)

    
res_header()


#
# def _add_custom_header(self, rml_dom, header='external'):
#     if header=='internal':
#         rml_head =  self.rml_header2
#     elif header=='internal landscape':
#         rml_head =  self.rml_header3
#     elif header=='external':
#         rml_head =  self.rml_header
#     else:
#         header_obj= self.pool.get('res.header')
#         rml_head_id = header_obj.search(self.cr,self.uid,[('name','=',header)])
#         if rml_head_id:
#             rml_head = header_obj.browse(self.cr, self.uid, rml_head_id[0]).rml_header
#     try:
#         head_dom = etree.XML(rml_head)
#     except:
#         raise osv.except_osv(_('Error in report header''s name !'), _('No proper report''s header defined for the selected report. Check that the report header defined in your report rml_parse line exist in Administration/reporting/Reporting headers.' ))
#
#     for tag in head_dom:
#         found = rml_dom.find('.//'+tag.tag)
#         if found is not None and len(found):
#             if tag.get('position'):
#                 found.append(tag)
#             else :
#                 found.getparent().replace(found,tag)
#     return True
#
# report_sxw.rml_parse._add_header = _add_custom_header