# -*- coding: utf-8 -*-
{
    'name': "Stock Ventacero",

    'summary': """Stock Ventacero""",

    'description': """Stock Ventacero""",

    'author': "Assetel",
    'website': "http://www.assetel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'delivery', 'stock', 'delivery', 'l10n_mx_edi_extended', 'purchase_ventacero', 'stock_picking_batch'],

    # always loaded
    'data': [
        'views/product_product.xml',
        'views/product_template.xml',
        'views/report_picking.xml',
        'views/stock_backorder_confirmation.xml',
        'views/stock_location.xml',
        'views/stock_move_line.xml',
        'views/stock_move.xml',
        'views/stock_picking_type.xml',
        'views/stock_picking.xml',
        'views/stock_quant.xml',
        'views/stock_return_picking.xml',
        'views/stock_valuation_layer.xml',
        'views/stock_warehouse_orderpoint.xml',
        'views/stock_warehouse.xml',
        'report/report_replenishment_header_inherit.xml',
        
        
    ],

    'assets': {
        'web.assets_backend': [
            'stock_ventacero/static/src/js/counted_quantity_uom_p_widget.js',
        ],
    },
}