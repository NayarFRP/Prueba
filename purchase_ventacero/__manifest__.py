# -*- coding: utf-8 -*-
{
    'name': "Purchase Ventacero",

    'summary': """Purchase Ventacero""",

    'description': """Purchase Ventacero""",

    'author': "Assetel",
    'website': "http://www.assetel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase', 'delivery', 'stock'],

    # always loaded
    'data': [
        'views/account_move.xml',
        'views/purchase_order.xml',
        'views/report_delivery_document.xml',
        'views/report_purchaseorder_document.xml',
        'views/stock_move_line.xml',
        'views/stock_move.xml',
        'views/stock_picking.xml',
        'views/stock_valuation_layer.xml',
    ],
}