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

from osv import osv, fields

class report_choose_hearder(osv.osv_memory):
    _name = 'report.choose.hearder'
    _description = 'Report choose hearder'

    _columns = {
       # 'header': fields.many2one('header', 'Header', required = True, help="Page Header"),
       'header': fields.char('header', size=32,  help="Page Header"),
        }
    _defaults={
        'header':'internal',
    }

    def check_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        active_model=context.get('active_model',[])
        # data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
            'ids': context.get('active_ids',[]),
            'model': active_model,
            # 'form': data
        }
        if active_model == 'account.invoice':
            selected_obj = context.get('active_id',False) and \
                           self.pool.get(active_model).browse(cr, uid, context.get('active_id',False), \
                                                              context=context) or False
            if selected_obj and selected_obj.efcs:
                return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'account.invoice.layout.efcs',
                    'datas': datas,
                    'context':context,
                    }
            else:
                return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'account.invoice.layout2',
                    'datas': datas,
                    'context':context,
                    }

        if active_model == 'stock.picking.out':
            selected_obj = context.get('active_id',False) and \
                           self.pool.get(active_model).browse(cr, uid, context.get('active_id',False), \
                                                              context=context) or False
            if selected_obj and selected_obj.state =='done':
                if selected_obj and selected_obj.efcs:
                    return {
                        'type': 'ir.actions.report.xml',
                        'report_name': 'stock.picking.list.layout.out.efcs',
                        'datas': datas,
                        'context':context,
                        }
                else:
                    return {
                        'type': 'ir.actions.report.xml',
                        'report_name': 'stock.picking.list.layout.out2',
                        'datas': datas,
                        'context':context,

                        }
            else:
                return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'stock.picking.list.layout.out.without_logo',
                    'datas': datas,
                    'context':context,
                    }


    def check_report_grouped(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        active_model=context.get('active_model',[])
        # data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
            'ids': context.get('active_ids',[]),
            'model': active_model,
            # 'form': data
        }

        if active_model == 'account.invoice':
            selected_obj = context.get('active_id',False) and \
                               self.pool.get(active_model).browse(cr, uid, context.get('active_id',False), \
                                                                       context=context) or False
            if selected_obj and selected_obj.efcs:
                return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'invoice.layout.grouped.efcs',
                    'datas': datas,
                    'context':context,
                    }
            else:
                return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'invoice.layout.grouped',
                    'datas': datas,
                    'context':context,

                    }
        if active_model == 'stock.picking.out':
            selected_obj = context.get('active_id',False) and \
                           self.pool.get(active_model).browse(cr, uid, context.get('active_id',False), \
                                                              context=context) or False
            if selected_obj and selected_obj.efcs:
                return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'invoice.layout.grouped.efcs',
                    'datas': datas,
                    'context':context,
                    }
            else:
                return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'invoice.layout.grouped',
                    'datas': datas,
                    'context':context,

                    }


    def onchange_header(self, cr, uid, ids, header, context=None):

        return self.check_report(cr,uid,ids,context=context)



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: