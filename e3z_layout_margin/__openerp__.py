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


{
    'name': 'Ehanced views Layouts',
    'version': '1.0',
    "category": "Sales Management",
    'complexity': "easy",
    'description': """
This module ehance views created by layout module with fields/columns for margin.

    """,
    'author': 'valentin chemiere vchemiere@elanz.fr',
    'website': 'http://openelanz.com',
    'depends': ['sale_layout', 'sale_margin', 'e3z_lead_sale_ipbox'],
    'init_xml': [],
    'update_xml': [
        'sale_view.xml',
    ],
    'css': ['static/src/css/orderline.css'],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
