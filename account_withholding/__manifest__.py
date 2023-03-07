# -*- coding: utf-8 -*-
{
    'name': "Account Withholding ",

    'summary': """
        Adds Integration with withholding.""",

    'description': """
        Adds Integration with withholding.
    """,

    'author': "Conflux",
    'website': "https://conflux.pe",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '15.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/account_move_view.xml',
        'wizard/account_payment_register_views.xml',
        #'views/report_invoice.xml',
    ]
}