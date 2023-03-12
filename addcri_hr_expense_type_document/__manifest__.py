# -*- coding: utf-8 -*-
{
    'name': "Gastos tipo de documento",
    'version': '1.0',
    'summary': 'Añade campo tipo de documento',
    'description': """Add  field, type document """,
    'author': "HTE",
    'category': 'Uncategorized',
    'depends': ['hr','l10n_latam_invoice_document'],

    'data': [
        # 'security/ir.model.access.csv',
        'data/account_tax.xml',
        'views/l10n_latam_document_type_views.xml',
        'views/hr_expense_views.xml',
        
    ],
    'installable':True,
    'application':False
}
