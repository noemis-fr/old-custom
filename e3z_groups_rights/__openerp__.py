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


{
    'name': 'Groups rights',
    'version': '1.0',
    'category': 'Tools',
    'description': """
    Customize views by groups
""",
    'author': 'Elanz Centre',
    'website': 'http://www.openelanz.com',
    'summary': 'Leads and sales customizing',
    'depends': ['base', 'sale', 'stock', 'purchase', 'account', 'account_voucher', 'mrp_move_direct', 'e3z_lead_sale_ipbox', 'crm_helpdesk'],
    'data': [
        'sale_view.xml',
        'account_view.xml',
        'purchase_view.xml',
        'partner_view.xml',
        'stock_view.xml',
        'security/ir.model.access.csv',
    ],
    'css': [
        'static/src/css/groups_rights.css',
    ],
    'images': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
