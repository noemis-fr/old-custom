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
    'name': 'e3z_export_sage_conf_ipbox',
        'version': '1.0',
        'category': 'Account management',
        'description': """

Module de configuration Export Sage pour Le IPBOX
==========================================================

Ce module permet Configuration des de la comptabilité pour l'export  vers Sage.


            """,
        'author': 'Elanz Centre',
        'website': 'http://www.openelanz.com',
        'depends': [

                    'asgard_ledger_export',
        ],
        'data': [
            'import/sage_export_ipbox_prod.xml',
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
