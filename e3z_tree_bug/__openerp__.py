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
    'name': 'Show a bug on tree view',
    'version': '1.0',
    'category': 'Tools',
    'description': """
    Step to reproduce the bug:
    1- When this module is installed go on sales
    2- Create a new sale order
    3- Add a sale line with a product and qty 15, the field name and price_unit are locked, it's ok.
    4- Edit the previous added line to put 5 qty and tab to next field, the field name and price_unit should be unlocked, it's done but the display was completly glitched.
    http://tof.canardpc.com/view/de3163e3-1d4f-4f78-a2ec-245c75ad08f2.jpg
""",
    'author': 'Elanz Centre',
    'website': 'http://www.openelanz.com',
    'summary': 'Leads and sales customizing',
    'depends': ['base', 'sale'
    ],
    'data': [
        'sale_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
