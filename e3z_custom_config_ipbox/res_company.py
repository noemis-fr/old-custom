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

__author__ = 'vvayssiere'
import openerp
from openerp.osv import fields, orm
from openerp import SUPERUSER_ID, tools
from openerp.osv import fields, osv
import os
class res_company(orm.Model):
    _inherit = 'res.company'

    def get_custom_logo(self, cr, uid, ids, module="e3z_report_ipbox", img_path="image",file_name="company_logo.png"):
        imgdir = openerp.modules.get_module_resource(module,img_path);
        return open(os.path.join( os.path.abspath(imgdir), file_name), 'rb') .read().encode('base64')

    def set_logo (self, cr, uid, ids,  module="e3z_report_ipbox", img_path="image",\
                    file_name="company_logo.png", field='logo', context={}):
        img = self.get_custom_logo(cr, uid, ids,  module=module, img_path=img_path, file_name=file_name)
        self.write(cr,uid,ids,{field:img}, context=context)
        return True