# -*- coding: utf-8 -*-
# Copyright (C) 2022 - Myrrkel (https://github.com/myrrkel).
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
import openai

_logger = logging.getLogger(__name__)


class OpenAiMixin(models.AbstractModel):
    _name = 'openai.mixin'
    _description = 'OpenAI Mixin'

    def get_openai(self):
        openai.api_key = self.env['ir.config_parameter'].sudo().get_param('openai_api_key')
        if not openai.api_key:
            raise UserError(_('OpenAI API key is required.'))
        return openai
