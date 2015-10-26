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

{
    'name': 'e3z_custom_config_noemis',
        'version': '1.0',
        'category': 'Sales Management',
        'description': """
Paramétrage structurant pour Demo
=================================

Ce module permet d'intégrer le paramétrage structurant pour Dlice en inmportant les données suivantes:

* import/res.partner.csv : paramétrage partenaires liés aux sociétés du client

* import/res.company.csv : paramétrage des société du client
 
* import/stock.location.csv : paramétrage des emplacements structurant

* import/stock.warehouse.csv : paramétrage des entrepôts
 
* import/sale.shop.csv : paramétrage des magasins
 
* import/account.journal.csv : paramétrage des méthodes des journaux

* import/product.category.csv : paramétrage des catégories d'articles

""",
        'author': 'Elanz Centre',
        'website': 'http://www.openelanz.com',
        'depends': ['base', 'base_report_header', ],
                    # 'e3z_setup_ipbox'],
        'data': [
            # Pas d'import de config sur la base de prod (à commenter tous les imports une fois le parametrage est fait)
            # 'import/res.partner.csv',
            # 'import/ir.sequence.csv',
            # 'import/res.company.csv',
            # 'import/stock_data.xml',
            # 'import/stock.location.csv',
            # 'import/stock.warehouse.csv',
            # 'import/sale.shop.csv',
            # 'import/res.users.csv',  # à compléter par users
            # 'import/res.groups.csv',  # à compléter en fonction des profils les groupes
            # 'import/account.account.csv',
            # 'import/account.account.xml', #pour eviter le problème de re-import utiliser
            # 'import/product.category.csv',
            # 'import/account.journal.csv',
            # 'import/product.tag.csv',
            # 'import/product.product.csv',
            # 'import/res.partner.csv',
            # 'import/res.partner.supplierinfo.csv',
            # 'import/delivery.carrier.csv',
            # 'import/delivery.grid.csv',
            # 'import/delivery.grid.line.csv',
            # 'import/account.tax.code.csv',
            # 'import/account.tax.csv',
            # 'import/account.fiscal.position.csv',
            # 'import/account.fiscal.position.tax.csv',
            # 'import/account.fiscal.position.account.csv',
            # 'import/pos.config.csv', pas pos
            # 'import/res.country.csv', à utiliser uniquement si le module account_fiscal_position_country est installé
            # 'import/account_minimal.xml',
            # 'compute_parent_left_right.yml',
            # 'account_config_settings.yml',
            'company_settings.yml',


        ],
        'demo':
            [
        ],
        'test':
            [
        ],
        'installable':
            True,
        'auto_install':
            False,
        "active": False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
