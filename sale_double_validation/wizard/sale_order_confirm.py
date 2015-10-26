##############################################################################
#
#    Agaplan 
#    Copyright (C) 2004-2013 Agaplan NV (www.agaplan.eu)
#    @author Peter Langenberg
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

from openerp.osv import osv, fields
from openerp.tools.translate import _

class sale_validate_order(osv.Model):
		_name = "sale.validate.order"
		_description = "Validate quote"
		_columns = {
			'sale_ids': fields.many2many('sale.order', 'sale_confirm_wiz_rel', 'wiz_id', 'sale_id', string='Sales to confirm'),
			}
		_defaults = {
			'sale_ids': lambda self,cr,uid,context: context.get('active_ids'),
		}

		def view_init(self, cr, uid, fields_list, context=None):
			if context is None:
				context = {}
			record_ids = context and context.get('active_ids',False)
			for order in self.pool.get('sale.order').browse(cr,uid,record_ids, context=context):
				if order.state !='draft' and order.state != 'sent':
					raise osv.except_osv(_('Warning'), _('You can only confirm quotes'))
			return False

		def validate_orders(self, cr, uid, ids, context=None):
			if context is None:
				context = {}
			for wiz in self.browse(cr, uid, ids, context=context):
				record_ids = context and context.get('active_ids',False)
				for order in wiz.sale_ids:
					if order.state == 'draft' or order.state == 'sent':
						order.action_button_confirm(context=None)
				return False