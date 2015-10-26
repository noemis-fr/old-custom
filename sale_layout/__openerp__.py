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

{
    "name" : "Sales Orders Print Layout",
    "version" : "1.1",
    "images" : ["images/sale_order_layout.png", "images/sale_order_line_layout.png", "images/elanz_logo.png"],
    "depends" : ["sale", "sale_stock", "account_invoice_layout"],
    "author" : "OpenERP SA/Elanz Centre",
    'complexity': "easy",
    "description": """
This module provides features to improve the layout of the Sales Order.
=======================================================================

It gives you the possibility to
    * order all the lines of a sales order
    * add titles, comment lines, sub total lines
    * put page breaks

Line type code:
P: product, a classic line like standard
T: title, a text in bold
R: remark, simple text
STl: subtotal, price subtotal of all lines above
SP: split page, a split for print.

This addon is an adaptation from openerp 6 to openerp 7.
    """,
    "website" : "http://www.openelanz.com",
    "category" : "Sales Management",
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
        "sale_layout_view.xml",
        "sale_layout_report.xml",
    ],
    "test" : ['test/sale_layout_report.yml'],
    "auto_install": False,
    "installable": True,
    # "certificate" : "00982333536005187677",
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
