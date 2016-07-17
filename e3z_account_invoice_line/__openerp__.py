# -*- coding: utf-8 -*-
# Copyright (C) 2012-2013 Elanz (<http://www.openelanz.fr>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Account invoice lines menus',
    'version': '1.0',
    'category': 'Tools',
    'author': 'Elanz Centre',
    'website': 'http://www.openelanz.com',
    'summary': 'Account invoice lines menus',
    'description': """
===========================
Account Invoice line module
===========================

* provide two extra menu for account invoice lines in accounting part
  to make statistic.

* Add a field 'project_code' on sale order, copied on invoice line.
""",
    'depends': [
        'account',
        'sale',
        'e3z_account_ipbox',
    ],
    'data': [
        'views/view_sale_order.xml',
        'views/view_account_invoice_line.xml',
        'views/action.xml',
        'views/menu.xml',
    ],
}
