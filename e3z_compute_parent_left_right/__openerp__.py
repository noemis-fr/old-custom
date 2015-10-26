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
    'name': 'Compute parent left and parent right',
    'version': '1.0',
    'category': 'Tools',
    'description': """
    This module allows to compute parent left and parent right for models ex : account.account, product.category, ....
""",
    'author': 'EL HADJ MIMOUNE/ Elanz Centre',
    'website': 'http://openelanz.fr',
    'summary': 'Tools',
    'depends': [
        'web',
    ],
    'data': ['wizard/compute_parent_wizard_view.xml',
             "security/ir.model.access.csv"],
    'images': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
