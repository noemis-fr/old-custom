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
{
    'name': 'Sale to Invoice layout relation',
    'version': '0.1',
    'category': 'Generic Modules/Others',
    'description': """
    ITA: Questo modulo permette di generare anche le righe di intestazione, titolo e testo quando si crea una fattura da un ordine di vendita avente layout gestiota da sale_layout
    ENG: This module also allows you to create header rows, title and text when you create an invoice from a sales order with layout managed by sale_layout
    """,
    'author': 'www.andreacometa.it',
    'website': 'http://www.andreacometa.it',
    'license': 'AGPL-3',
    "active": False,
    "installable": True,
    "depends" : ['sale_layout','account_invoice_layout',],
    "update_xml" : [],
}
