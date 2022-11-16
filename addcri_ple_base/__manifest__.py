{
    'name': 'Base registro de compras y ventas PLE',
    'version': '1.0.202209261',
    'description': '',
    'summary': '',
    'author': 'Jhon Jairo Rojas Ortiz',
    'website': '',
    'license': 'LGPL-3',
    'category': '',
    'depends': [
        'base', 'account', 'l10n_latam_base', 'addcri_exchange_rate_purchase', 'addcri_detraction_retention_payment', 'addcri_not_domiciled'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_journal.xml',
        'views/account_move.xml',
        'views/account_retention.xml',
        'views/code_customs.xml',
        'views/res_company.xml',
        "views/ple_base.xml"
    ],
    'demo': [

    ],
    'auto_install': False,
    'application': True,
    'assets': {

    }
}
