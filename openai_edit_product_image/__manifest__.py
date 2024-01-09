# -*- coding: utf-8 -*-
# Copyright (C) 2023 - Michel Perrocheau (https://github.com/myrrkel).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/algpl.html).
{
    'name': 'OpenAI Edit Product Image',
    'version': '16.1.0.0',
    'author': 'Michel Perrocheau',
    'website': 'https://github.com/myrrkel',
    'summary': "Generate a new product image from a cropped product image with DALL-E",
    'sequence': 0,
    'certificate': '',
    'license': 'AGPL-3',
    'depends': [
        'openai_connector',
        'product',
        'sale',
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
        'data/prompt_templates.xml',
        'data/openai_edit_data.xml',
        'views/openai_product_result_views.xml',
        'views/product_views.xml',
    ],
    'auto_install': False,
    'installable': True,
    'application': False,
}
