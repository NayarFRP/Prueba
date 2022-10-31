# -*- coding: utf-8 -*-
{
    'name': "POS Ventacero",

    'summary': """POS Ventacero""",

    'description': """POS Ventacero""",

    'author': "Assetel",
    'website': "http://www.assetel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'point_of_sale', 'pos_restaurant'],

    # always loaded
    'data': [
        
    ],
    'assets': {
        'web.assets_backend': [
            'pos_ventacero/static/src/js/**/*',
        ],
        'web.assets_qweb': [
            'pos_ventacero/static/src/xml/**/*',
        ],
    },
    'auto_install': True,
}
