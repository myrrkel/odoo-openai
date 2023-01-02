# -*- coding: utf-8 -*-
# Copyright (C) 2022 - Myrrkel (https://github.com/myrrkel).
# License GPL-3.0 or later (https://www.gnu.org/licenses/gpl.html).
{
    'name': 'OpenAI Connector',
    'version': '16.0.0.0',
    'author': 'Myrrkel',
    'website': 'https://github.com/myrrkel',
    'summary': "This module adds a connector for OpenAI API",
    'sequence': 0,
    'certificate': '',
    'license': 'GPL-3',
    'depends': [
        'base',
        'mail',
    ],
    'external_dependencies': {
        'python': ['openai'],
    },
    'category': 'OpenAI',
    'complexity': 'easy',
    'qweb': [
    ],
    'demo': [
    ],
    'images': [
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/res_config_settings_views.xml',
        'views/openai_completion_views.xml',
        'views/openai_completion_result_views.xml',
        'views/openai_edit_views.xml',
        'views/openai_edit_result_views.xml',
        'views/openai_image_views.xml',
        'views/openai_image_result_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'openai_connector/static/src/scss/style.scss',
        ],
    },

    'auto_install': False,
    'installable': True,
    'application': False,
}