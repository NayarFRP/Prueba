# -*- coding: utf-8 -*-
{
    'name': "Contabilidad Ventacero",

    'summary': """Contabilidad Ventacero""",

    'description': """Contabilidad Ventacero""",

    'author': "Assetel",
    'website': "http://www.assetel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale_management', 'account', 'account_accountant', 'account_asset', 'point_of_sale', 'l10n_mx_edi'],

    # always loaded
    'data': [
        'views/account_asset.xml',
        'views/account_journal.xml',
        'views/account_move.xml',
        'views/credit_note_reasons_menu.xml',
        'views/credit_note_reasons.xml',
        'views/purchase_order.xml',
        'views/res_partner.xml',
        'views/res_users.xml',
        'views/sale_order.xml',
    ],
}

