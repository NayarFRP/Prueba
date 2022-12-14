# -*- coding: utf-8 -*-
{
    'name': "Expense Ventacero",

    'summary': """
        Expense Ventacero""",

    'description': """
        Expense Ventacero
    """,

    'author': "Assetel",
    'website': "http://www.assetel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_expense', 'account_accountant'],

    # always loaded
    'data': [
        'views/account_journal.xml',
        'views/hr_employee.xml',
        'views/hr_expense_sheet.xml',
        'views/hr_expense_sheet_menu.xml',
        'views/hr_expense.xml',
    ],
}
