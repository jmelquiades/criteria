# -*- coding: utf-8 -*-
{
    'name': "ADDCRI - RUC SEARCH",
    'version': '0.1',
    'author': "Kokox",
    'category': 'Generic Modules/Base',
    'summary': "Validador de RUC para SUNAT",
    'license': 'LGPL-3',
    'contributors': [
        'Jorge Aguilar <jorge_eje18@hotmail.com>'
    ],
    'description': """
        Addon buscador de RUC en SUNAT.
    """,
    'website': "https://www.linkedin.com/in/jorgeaguilarsomoza/",
    'depends': ['l10n_latam_base','l10n_pe'],
    'data': [
        # 'security/ir.model.access.csv',
        #'views/views.xml',
        #'views/templates.xml',
        'views/res_partner_view.xml',
        'views/res_config_settings_views.xml',
        'views/res_company_views.xml',
    ],
    # solo cargado en modo demostración
    'demo': [
        #'demo/demo.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'support': 'jorge_eje18@hotmail.com',
    'installable': True,
    'auto_install': False,
    "sequence": 1,
    
    'post_init_hook': '_addcri_rucsearch_init',
}
