# -*- coding: utf-8 -*-
##############################################################################
#
#   Copyright (c) 2013 Agaplan (www.agaplan.eu)
#   @author Peter Langenberg
#
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

{
    'name': 'sale order double validation',
    'version': '1.0.0',
    'category': '',
    'description': """
In some organisations people want an extra state between draft - send and confirmed.
This module adds state validated to sale order and puts also a menu extra in the sales
    """,
    'author': 'Agaplan',
    'website': 'http://www.agaplan.eu',
    'depends': ['sale_stock'],
    'init': [],
    'data': ['sale_view.xml','sale_workflow.xml'],
    'demo': [],
    'test': [],
    'installable': True,
    'active': False,
}
