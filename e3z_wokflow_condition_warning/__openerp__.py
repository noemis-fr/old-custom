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
    'name': 'Workflow Warning',
    'version': '1.0',
    'category': 'Tools',
    'description': """
Adds workflow wanrnig management.
==============================================
This module give you a possibility to make a warning message associated with workflow transition condition. 
It adds the  "message" field to workflow transition and a check box "display a message  if false".  
Thus one can modify transition condition and display to a user a message when condition is not satisfied. 
""",
    'author': 'Elanz Centre',
    'website': 'http://www.openelanz.com',
    'summary': 'Workflow customizing', 
    'depends': ['base',
    ],
    'data': ['wkf_warning_view.xml'],
    'images': ['elanz_workflow_activity.jpg',
               'elanz_workflow_transition.jpg'],
    'installable': True,
    'application': True,
    'auto_install': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
