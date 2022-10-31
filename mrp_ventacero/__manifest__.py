# -*- coding: utf-8 -*-
{
    'name': "Mrp Ventacero",

    'summary': """Mrp Ventacero""",

    'description': """Mrp Ventacero""",

    'author': "Assetel",
    'website': "http://www.assetel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mrp'],

    # always loaded
    'data': [
        'views/mrp_bom.xml',
        'views/mrp_production.xml',
    ],
}