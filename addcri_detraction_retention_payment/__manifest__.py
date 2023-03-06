{
    'name': 'Detracción y retención',
    'version': '1.0.202210241',
    'description': '',
    'summary': '',
    'author': 'Jhon Jairo Rojas Ortiz',
    'website': '',
    'license': 'LGPL-3',
    'category': '',
    'depends': [
        'account',
        'l10n_pe_edi_extended_detraction',
        'l10n_latam_invoice_document',
        'l10n_pe_edi_extended',
        'addcri_sunat_tables',
        'addcri_exchange_rate_purchase'
    ],
    'data': [
        # 'security/ir.model.access.csv',
        # * Retention
        # 'data/l10n_latam_table_10.xml',
        'views/retention/res_partner.xml',
        'views/retention/res_config_settings.xml',
        'views/retention/account_bank_statement.xml',
        # 'views/retention/l10n_latam_table_10.xml',
        'views/retention/account_move.xml',
        # * Detraction
        'views/detraction/account_move.xml',
        'views/detraction/account_payment_register.xml',
        'views/detraction/res_config_settings.xml',
        # * Base
        # 'views/account_move.xml'

    ],
    'demo': [

    ],
    'auto_install': False,
    'application': False,
    'assets': {

    }
}
