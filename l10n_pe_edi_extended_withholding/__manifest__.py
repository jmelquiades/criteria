# -*- coding: utf-8 -*-
{
    'name': "Perú Withholding - E-invoicing",
    'summary': """
        Adds Integration with withholding.""",
    'description': """
        Adds Integration with withholding.
    """,
    'author': "Conflux",
    'website': "https://conflux.pe",
    'category': 'Localization/Peru',
    'version': '15.0.1.0.0',
    'depends': ['l10n_pe_edi_extended','account_withholding'],

    # always loaded
    'data': [
        'views/account_move_view.xml',
        'views/account_journal_view.xml',
    ]
}