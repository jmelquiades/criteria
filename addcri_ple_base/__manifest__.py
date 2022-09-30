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
        'base', 'account', 'l10n_latam_base'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_journal.xml',
        'views/account_move.xml',
        'views/account_move_line.xml',
        'views/account_retention.xml',
        'views/code_customs.xml',
        'views/res_company.xml',
        'views/res_partner.xml',
        "views/ple_base.xml"
    ],
    'demo': [

    ],
    'auto_install': False,
    'application': False,
    'assets': {

    }
}
