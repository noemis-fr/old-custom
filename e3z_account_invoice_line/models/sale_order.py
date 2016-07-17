# -*- coding: utf-8 -*-
# Copyright (C) 2012-2013 Elanz (<http://www.openelanz.fr>).
# @author: rguillot
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp.osv import fields, orm


class SaleOrder(orm.Model):
    _inherit = 'sale.order'

    _columns = {
        'project_code': fields.char(
            string='Project Code', help="Tip here a free extra text that"
            " will be reported on invoice line"),
    }
