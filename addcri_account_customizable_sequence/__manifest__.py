# -*- coding: utf-8 -*-
{
    'name': "Secuencia personalizado de Compras/Ventas por diarios",
    'version': '1.0',
    'summary': 'Añade campos dos campos serie y secuencia ,crea una pestaña Localización PERU en los Diarios contables para poder asignar una secuecia y generar el Secuencial por Diario contable',
    'description': """Add two fields, series and sequence, create a PERU Location tab in the Accounting Journals to be able to assign a sequence and generate the Sequential by Accounting Journal""",
    'author': "HTE",
    'category': 'Uncategorized',
    'depends': ['account','l10n_latam_invoice_document'],

    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/account_journal_views.xml',
        'views/account_move_views.xml',
        'views/it_invoice_serie.xml',
        
    ],
    'installable':True,
    'application':False
}
