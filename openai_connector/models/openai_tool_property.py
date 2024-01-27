# Copyright (C) 2024 - Michel Perrocheau (https://github.com/myrrkel).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import json
from tempfile import NamedTemporaryFile
from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
from odoo.addons.base.models.ir_model import SAFE_EVAL_BASE

import logging

_logger = logging.getLogger(__name__)


class OpenAiToolProperty(models.Model):
    _name = 'openai.tool.property'
    _description = 'OpenAI Tool Property'

    def _get_tool_property_type_list(self):
        return [('string', _('String')),
                ('integer', _('Integer'))]

    name = fields.Char()
    tool_id = fields.Many2one('openai.tool', invisible=True)
    type = fields.Selection(selection=_get_tool_property_type_list)
    description = fields.Text()
    required = fields.Boolean()
