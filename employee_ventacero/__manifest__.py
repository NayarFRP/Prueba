# -*- coding: utf-8 -*-
{
    'name': "Employee Ventacero",

    'summary': """Employee Ventacero""",

    'description': """Employee Ventacero""",

    'author': "Assetel",
    'website': "http://www.assetel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'l10n_mx_edi_extended'],

    # always loaded
    'data': [
        'views/hr_employee.xml',
        'views/res_partner.xml',
    ],
}