# -*- coding: utf-8 -*-
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

__author__ = 'vchemiere'

from openerp.osv import osv, fields
import logging


_logger = logging.getLogger(__name__)


class ir_sequence(osv.osv):
    _inherit = 'ir.sequence'

    _columns = {
        'reset_zero': fields.boolean('Reset to zero', help='This sequence will be reset to 0 when the cron is triggered'),
    }

    def set2zero(self, cr, uid, context=None):
        sequence_obj = self.pool.get('ir.sequence')
        sequence_ids = sequence_obj.search(cr, uid, [('reset_zero', '=', True)])
        for sequence_id in sequence_ids:
            sequence = sequence_obj.browse(cr, uid, sequence_id)
            _logger.info('Reset sequence {} from {} to zero.'.format(sequence.name, sequence.number_next))
            sequence_obj._alter_sequence(cr, sequence_id, 1, 1)
            sequence_obj._set_number_next_actual(cr, uid, sequence_id, 'sale invoice', 1)
        return True