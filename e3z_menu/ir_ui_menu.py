# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2012 OpenERP SA (<http://openerp.com>).
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


class ir_ui_menu(osv.osv):
    _inherit = 'ir.ui.menu'

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        context = context or {}

        if not context.get('ir.ui.menu.full_list', False):
            args += [('visible', '=', True)]

        return super(ir_ui_menu, self).search(cr, uid, args,
                                              offset=0, limit=None, order=order, context=context, count=False)

    _columns = {
        'visible': fields.boolean('Visible')
    }

    _defaults = {
        'visible': True,
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
