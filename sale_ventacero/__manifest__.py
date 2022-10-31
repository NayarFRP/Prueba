# -*- coding: utf-8 -*-
{
    'name': "Sale Ventacero",

    'summary': """Sale Ventacero""",

    'description': """Sale Ventacero""",

    'author': "Assetel",
    'website': "http://www.assetel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale_management', 'stock', 'crm', 'payment_ventacero'],

    # always loaded
    'data': [
        'views/account_move_report.xml',
        'views/account_move.xml',
        'views/account_payment_register.xml',
        'views/crm_team.xml',
        'views/delivery_shift_menu.xml',
        'views/delivery_shift.xml',
        'views/product_template.xml',
        'views/report_saleorder_document.xml',
        'views/res_users.xml',
        'views/sale_order.xml',
        'views/stock_warehouse.xml',
        'views/wizard_change_date.xml',
    ],
}