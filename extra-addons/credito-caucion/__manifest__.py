{
    'name': 'TeCredit',
    'version': '17.0',
    'summary': 'Aplicación para la gestión de riesgos y crédito.',
    'category': 'Finance',
    'license': 'OPL-1',
    'version': '1.0',
    'author': 'Javier Sánchez Prieto',
    'website': 'http://www.tecletes.com',
    'depends': ['base', 'web', 'mail', 'contacts', 'account', 'sale'],
    'data': [
        'security/ir.model.access.csv',

        'views/sale_order_confirm_warning_views.xml',
        'views/res_config_settings_views.xml',

        'views/wizard_views.xml',

        'views/gestores_views.xml',

        'views/riesgo_clasificacion_views.xml',
        'views/account_move_line_views.xml',
        'views/riesgo_afp_views.xml',
        'views/riesgo_prorroga_views.xml',
        'views/riesgo_siniestro_views.xml',
        'views/riesgo_actividades_views.xml',
        'views/riesgo_alerta_views.xml',

        'views/riesgo_resultado_views.xml',
        'views/riesgo_views.xml',
        'views/riesgo_menus.xml',   
    ],
    'assets': {
        'web.assets_backend': [
            'credito-caucion/static/src/**/*.css',
            'credito-caucion/static/src/**/*.js',
            'credito-caucion/static/src/**/*.xml',
            'credito-caucion/static/src/**/*.scss',
        ],
    },
    'images': [
        'static/description/icon.png',
        'static/img/company_image.png',
    ],
    'installable': True,
    'application': True,
}
