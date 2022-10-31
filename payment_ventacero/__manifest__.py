# -*- coding: utf-8 -*-
{
    'name': "Payment Ventacero",

    'summary': """Payment Ventacero""",

    'description': """Payment Ventacero""",

    'author': "Assetel",
    'website': "http://www.assetel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account_accountant'],

    # always loaded
    'data': [
        'data/ir_sequence_data.xml',
        'views/account_journal.xml',
        'views/account_payment_batch_line.xml',
        'views/account_payment_batch_menu.xml',
        'views/account_payment_batch_report.xml',
        'views/account_payment_batch.xml',
        'views/res_partner_bank.xml',
    ],
}