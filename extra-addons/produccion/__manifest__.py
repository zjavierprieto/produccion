{
    'name': 'Credito y Caución Producción',
    'version': '17.0',
    'summary': 'Conector Oficial de Crédito y Caución',
    'category': 'Finance',
    'license': 'OPL-1',
    'version': '1.0',
    'author': 'TeCredit S.L.',
    'website': 'http://www.tecredit.com',
    'depends': ['base', 'mail', 'sale', 'account'],
    'data': [
        'security/cyc_security.xml',
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',

   
        'views/cyc_afp_views.xml',
        'views/cyc_classification_views.xml',
        'views/cyc_partner_views.xml',
        'views/cyc_contact_views.xml',
        'views/cyc_menu_views.xml',
    ],
    'images': [
        'static/description/icon.png',
        'static/src/img/company_image.png', # no hace falta
    ],
    'assets': {
        'web.assets_backend': [
            'produccion/static/src/css/custom_kanban.css',
        ],
    },
    'installable': True,
    'application': True,
}
