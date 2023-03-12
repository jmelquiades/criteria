# -*- coding: utf-8 -*-
{
    'name': "Reporte Libro Mayor",
    'version': '1.0',
    'summary': 'Reporte Libro Mayor',
    'description': """Reporte Libro Mayor""",
    'author': "HTE",
    'category': 'Uncategorized',
    # any module necessary for this one to work correctly
    'depends': ['account','account_accountant'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'views/main_menu.xml',
        'views/report_libro_mayor.xml',
        'views/template_report.xml',

        
    ],
    'installable':True,
    'application':False
}
