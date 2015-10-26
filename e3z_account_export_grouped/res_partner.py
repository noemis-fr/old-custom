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

from openerp import SUPERUSER_ID
from openerp.osv import osv, fields


class res_partner(osv.osv):
    _name = 'res.partner'
    _inherit = 'res.partner'
    _columns = {
        'country_id': fields.many2one('res.country', 'Country', required=True,),
    }
    def create(self, cr, uid, vals, context=None):
        if vals.get('is_company', False):
            if not vals.get('ref', False):
                if vals.get('country_id', False):
                    country = self.pool.get('res.country').browse(cr, uid, vals.get('country_id'), context=context)
                    country = country.property_account_position and country.property_account_position.id or False
                    sequence = 'seq_export_fr'
                    if country == 1:
                        sequence = 'seq_export_cee'
                    elif country == 2:
                        sequence = 'seq_export_export'

                    vals['ref'] = self.pool.get('ir.sequence').get(cr, uid, sequence) or False

        return super(res_partner, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        for partner in self.browse(cr, uid, ids, context):
            if partner.is_company:
                if not vals.get('ref', False):
                    if vals.get('ref') is False or not partner.ref:
                        if vals.get('country_id', False) or partner.country_id:
                            if vals.get('country_id', False):
                                country = self.pool.get('res.country').browse(cr, uid, vals.get('country_id'), context=context)
                            else:
                                country = partner.country_id
                            country = country.property_account_position and country.property_account_position.id or False
                            sequence = 'seq_export_fr'
                            if country == 1:
                                sequence = 'seq_export_cee'
                            elif country == 2:
                                sequence = 'seq_export_export'

                            vals['ref'] = self.pool.get('ir.sequence').get(cr, uid, sequence) or False

        return super(res_partner, self).write(cr, uid, ids, vals, context=context)

    def write_mass(self, cr, uid, ids, vals, context=None):
        for partner in self.browse(cr, uid, ids, context):
            if partner.is_company:
                if partner.country_id:
                    country = partner.country_id
                    country = country.property_account_position and country.property_account_position.id or False
                    sequence = 'seq_export_fr'
                    if country == 1:
                        sequence = 'seq_export_cee'
                    elif country == 2:
                        sequence = 'seq_export_export'

                    vals['ref'] = self.pool.get('ir.sequence').get(cr, uid, sequence) or False

        return super(res_partner, self).write(cr, uid, ids, vals, context=context)