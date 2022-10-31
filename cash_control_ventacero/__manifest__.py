# -*- coding: utf-8 -*-
{
    'name': "Cash control Ventacero",

    'summary': """Cash control Ventacero""",

    'description': """Cash control Ventacero""",

    'author': "Assetel",
    'website': "http://www.assetel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account_accountant', 'sale_management', 'sale_ventacero'],

    # always loaded
    'data': [
        'views/account_cash_control_menu.xml',
        'views/account_cash_control.xml',
        'views/account_journal.xml',
        'views/crm_team.xml',
        'views/res_users.xml',
        'views/wizard_cash_control_close.xml',
        'views/wizard_cash_control_in.xml',
        'views/wizard_cash_control_open.xml',
        'views/wizard_cash_control_out.xml',
    ],
}