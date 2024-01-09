# -*- coding: utf-8 -*-
# Copyright (C) 2023 - Michel Perrocheau (https://github.com/myrrkel).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/algpl.html).
{
    'name': 'OpenAI Chat',
    'version': '17.0.1.0',
    'author': 'Michel Perrocheau',
    'website': 'https://github.com/myrrkel',
    'summary': "Add a AI Bot user to chat with like in ChatGPT",
    'sequence': 0,
    'certificate': '',
    'license': 'AGPL-3',
    'depends': [
        'openai_connector',
        'mail',
        'bus',
    ],
    'category': 'Community',
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
        'data/openai_chat_data.xml',
        'data/openai_completion_data.xml',
    ],
    'assets': {
        'web.assets_backend': {
            'openai_chat/static/src/core/*',
        },
    },
    'auto_install': False,
    'installable': True,
    'application': False,
}
