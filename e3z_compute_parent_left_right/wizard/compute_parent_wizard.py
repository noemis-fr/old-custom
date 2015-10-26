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

""" Wizard computing parent left, parent right for object with parent_id field"""

from openerp.osv.orm import TransientModel, fields


class compute_parent_left_right(TransientModel):
    _name = 'compute.parent.left.right'
    _description = 'Compute parent left right'

    _columns = {'model': fields.many2one(
                        'ir.model', required=True,
                        string='Model')
    }


    def action_compute_parent(self, cr, uid, wiz_id, context=None):
        """ action to computer parent left and right parent for model"""
        if isinstance(wiz_id, list):
            wiz_id = wiz_id[0]
        current = self.browse(cr, uid, wiz_id, context=context)
        model_def = current['model']
        model_obj = self.pool.get(model_def.model)
        model_obj._parent_store_compute(cr)
        return True

