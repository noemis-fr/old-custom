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
from openerp.addons.product import product
import re


class product_product(osv.osv):
    _inherit = 'product.product'

    _columns = {
        'purchase_price': fields.float('Purchase Price'),
    }

def name_get2(self, cr, user, ids, context=None):
    if context is None:
        context = {}
    if isinstance(ids, (int, long)):
        ids = [ids]
    if not len(ids):
        return []
    def _name_get(d):
        name = d.get('name','')
        code = d.get('default_code',False)
        if code:
            if context.get('search', False):
                name = '[%s] %s' % (code,name)
            else:
                name = '%s' % (code)
        if d.get('variants'):
            name = name + ' - %s' % (d['variants'],)
        return (d['id'], name)

    partner_id = context.get('partner_id', False)

    result = []
    for product in self.browse(cr, user, ids, context=context):
        sellers = filter(lambda x: x.name.id == partner_id, product.seller_ids)
        if sellers:
            for s in sellers:
                mydict = {
                          'id': product.id,
                          'name': s.product_name or product.name,
                          'default_code': s.product_code or product.default_code,
                          'variants': product.variants
                          }
                result.append(_name_get(mydict))
        else:
            mydict = {
                      'id': product.id,
                      'name': product.name,
                      'default_code': product.default_code,
                      'variants': product.variants
                      }
            result.append(_name_get(mydict))
    return result

product.product_product.name_get = name_get2

def name_search2(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
    if not args:
        args = []
    if name:
        ids = self.search(cr, user, [('default_code','=',name)]+ args, limit=limit, context=context)
        if not ids:
            ids = self.search(cr, user, [('ean13','=',name)]+ args, limit=limit, context=context)
        if not ids:
            # Do not merge the 2 next lines into one single search, SQL search performance would be abysmal
            # on a database with thousands of matching products, due to the huge merge+unique needed for the
            # OR operator (and given the fact that the 'name' lookup results come from the ir.translation table
            # Performing a quick memory merge of ids in Python will give much better performance
            ids = set()
            ids.update(self.search(cr, user, args + [('default_code',operator,name)], limit=limit, context=context))
            if not limit or len(ids) < limit:
                # we may underrun the limit because of dupes in the results, that's fine
                ids.update(self.search(cr, user, args + [('name',operator,name)], limit=(limit and (limit-len(ids)) or False) , context=context))
            ids = list(ids)
        if not ids:
            ptrn = re.compile('(\[(.*?)\])')
            res = ptrn.search(name)
            if res:
                ids = self.search(cr, user, [('default_code','=', res.group(2))] + args, limit=limit, context=context)
    else:
        ids = self.search(cr, user, args, limit=limit, context=context)
    context.update({'search': True})
    result = self.name_get(cr, user, ids, context=context)
    return result

product.product_product.name_search = name_search2
