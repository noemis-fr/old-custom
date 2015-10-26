# -*- encoding: utf-8 -*-
##############################################################################
#
#    Personalizzazione realizzata da Francesco OpenCode Apruzzese
#    Compatible with OpenERP release 6.0.0
#    Copyright (C) 2010 Andrea Cometa. All Rights Reserved.
#    Email: cescoap@gmail.com, info@andreacometa.it
#    Web site: http://www.andreacometa.it
#
##############################################################################
from osv import fields, osv

class sale_order_line(osv.osv):

	_name = "sale.order.line"
	_inherit = "sale.order.line"

	def invoice_line_create(self, cr, uid, ids, context=None):
		new_ids = []
		list_seq = []
		order_ids = []
		# -----
		# PRIMO CICLO CHE GENERA I PRODOTTI REALI
		for line in self.browse(cr, uid, ids, context=context):
			if line.layout_type == 'article':
				new_ids.append(line.id)
				list_seq.append(line.sequence)
				if not line.order_id.id in order_ids:
					order_ids.append(line.order_id.id)
		invoice_line_ids = super(sale_order_line, self).invoice_line_create(cr, uid, new_ids, context)
		pool_inv_line = self.pool.get('account.invoice.line')
		seq = 0
		for obj_inv_line in pool_inv_line.browse(cr, uid, invoice_line_ids, context=context):
			pool_inv_line.write(cr, uid, [obj_inv_line.id], {'sequence': list_seq[seq]}, context=context)
			seq += 1
		# SECONDO CICLO CHE GENERA LE RIGHE FITTIZIE
		order_obj = self.pool.get('sale.order')
		order_browses = order_obj.browse(cr, uid, order_ids)
		for order in order_browses:
			for line in order.abstract_line_ids:
				if line.layout_type in ('title', 'text', 'subtotal'):
					inv_id = pool_inv_line.create(cr, uid, {
						'name' : line.name,
						'state' : line.layout_type,
						'sequence' : line.sequence,
						'origin' : order.name,})
					invoice_line_ids.append(inv_id)
				elif line.layout_type in ('line', 'break'):
					inv_id = pool_inv_line.create(cr, uid, {
						'state' : line.layout_type,
						'sequence' : line.sequence,
						'origin' : order.name,})
					invoice_line_ids.append(inv_id)
		return invoice_line_ids

sale_order_line()
