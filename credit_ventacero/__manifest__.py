# -*- coding: utf-8 -*-
{
    'name': "Credit Ventacero",

    'summary': """Credit Ventacero""",

    'description': """Credit Ventacero""",

    'author': "Assetel",
    'website': "http://www.assetel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'project', 'sale_management', 'account', 'account_accountant'],

    # always loaded
    'data': [
        'data/mail_activity_data.xml',
        'views/approval_criteria_menu.xml',
        'views/approval_criteria.xml',
        'views/res_config_settings.xml',
        'views/res_partner.xml',
        'views/sale_order.xml',
    ],
}