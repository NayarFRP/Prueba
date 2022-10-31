# -*- coding: utf-8 -*-
{
    'name': "Reports Ventacero",

    'summary': """Reports Ventacero""",

    'description': """Reports Ventacero""",

    'author': "Assetel",
    'website': "http://www.assetel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'stock_account', 'stock_ventacero', 'contacts', 'analytic'],

    # always loaded
    'data': [
        'views/purchase_order_line.xml',
        'views/purchase_order_line_menu.xml',
        'views/report_picking_batch.xml',
        'views/res_partner.xml',
        'views/sale_order_line.xml',
        'views/sale_order_line_menu.xml',
        'views/stock_move.xml',
        'views/stock_move_menu.xml',
        'views/stock_picking_batch.xml',
        'views/stock_picking.xml',
        'views/stock_picking_menu.xml',
        'views/stock_quant.xml',
        'views/stock_quant_menu.xml',
        'views/stock_valuation_layer.xml',
        'views/stock_valuation_layer_menu.xml',
    ],
}