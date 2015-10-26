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

from openerp.osv import fields,osv


class wkf_transition(osv.osv):
    """ Inherits wkf_transition and adds warning message capability"""
    _inherit = "workflow.transition"

    _columns = {
        'display_msg' : fields.boolean('Display warning message'),
        'notcondition_msg': fields.text('Message if not Condition', translate=True, 
                                 help="Warning message to be displayed if expression condition is not satisfied"),

    }
    _defaults = {
        'display_msg': False,
    }
wkf_transition()