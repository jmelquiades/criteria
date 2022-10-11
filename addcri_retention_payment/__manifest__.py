{
    'name': 'Retención',
    'version': '1.0',
    'description': '',
    'summary': '',
    'author': 'Jhon Jairo Rojas Ortiz',
    'website': '',
    'license': 'LGPL-3',
    'category': '',
    'depends': [
        'account',
        'l10n_latam_invoice_document'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/l10n_latam_table_10.xml',
        'views/res_partner.xml',
        'views/res_config_settings.xml',
        'views/account_bank_statement.xml',
        'views/l10n_latam_table_10.xml'
    ],
    'demo': [
    ],
    'auto_install': False,
    'application': False,
    'assets': {

    }
}
