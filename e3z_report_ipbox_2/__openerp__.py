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
    'name': 'Report sale, stock and account (2)',
    'version': '1.0',
    'category': 'Tools',
    'description': """
Sale and Invoice report modifications
""",
    'author': 'Elanz Centre',
    'website': 'http://openelanz.fr',
    'summary': 'Tools',
    'depends': [
        'sale',
        'account',
        'delivery',
        'sale_order_title',
        'account_invoice_layout',
        'base_report_header',
        'e3z_lead_sale_ipbox',  #puvr field;
    ],
    'data': [
        'account_invoice_layout_report.xml',
        'delivery_report.xml',
        'purchase_report.xml',
        'account_invoice_layout_view.xml',
        'stock_view.xml',
        'sale_view.xml',
        'sale_report.xml',
        'data/email_template.xml',
    ],
}
