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
    'name': 'e3z_setup_ipbox',
        'version': '1.0',
        'category': 'Sales Management',
        'description': """

Module d'installation et de configuration pour Le projet IPBOX
==========================================================

Ce module permet d'installer tous les  modules utile au périmettre fonctionnel d'IPBOX( par dépendence).

Il aide à configurer le système à l'installation d'une nouvelle base de données.

La configuration incluse dans ce module (paramétrage N1) concerne :


* Installation de la langue

* Configuration des ventes

* Configuration des achats

* Configuration des entrepôts

* Configuration des de la comptabilité
            """,
        'author': 'MEM Elanz Centre',
        'website': 'http://www.openelanz.com',
        'depends': [
                    'base',
                    'account',
                    'account_accountant',
                    'account_chart',
                    'account_payment',
                    'account_voucher',
                    'base_iban',
                    'base_import',
                    'base_setup',
                    'board',
                    'contacts',
                    'decimal_precision',
                    'l10n_fr',
                    'l10n_fr_rib',
                    'mail',
                    'process',
                    'procurement',
                    'product',
                    'product_manufacturer',
                    'product_visible_discount',
                    'purchase',
                    'sale',
                    'sale_order_dates',
                    'sale_stock',
                    'stock',
                    'document',
                    'mass_editing',
                    'web',
                    'web_calendar',
                    'web_diagram',
                    'web_gantt',
                    'web_graph',
                    'web_kanban',
                    'web_shortcuts',
                    'web_tests',
                    'web_view_editor',
                    'mrp_move_direct',
                    'crm',
                    'sale_margin',
                    'account_followup',

        ],
        'data': [
            # 'translate_config_settings.yml',
            # 'sale_config_settings.yml',
            # 'purchase_config_settings.yml',
            # 'stock_config_settings.yml',
            # 'import/account_fiscalyear.xml',
        ],
        'demo':
            [
        ],
        'test':
            [
        ],
        'installable':
            True,
        'auto_install':
            False,
        "active": False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
