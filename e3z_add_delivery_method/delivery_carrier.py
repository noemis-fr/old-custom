# -*- coding: utf-8 -*-
# OpenERP, Open Source Management Solution
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

__author__ = 'rguillot'

from openerp.osv import osv, fields


class delivery_carrier(osv.osv):
    _inherit = 'delivery.carrier'

    _columns = {
        'default_in_sales': fields.boolean("Default delivery method", help="If checked, this delivery method will be added to sale order which have an amount inferior to 1500€"),
        'min_amount': fields.float('Minimum amount', help="Under this amount, the delivery carrier will be added to the sale order")
    }

    _defaults = {
        'min_amount': 1500
    }