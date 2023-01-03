# -*- coding: utf-8 -*-
# Copyright (C) 2022 - Myrrkel (https://github.com/myrrkel).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class OpenAiImageResult(models.Model):
    _name = 'openai.image.result'
    _description = 'OpenAI Image Result'
    _inherit = ['openai.result.mixin']

    image_id = fields.Many2one('openai.image', string='Image', readonly=True, ondelete='cascade')
    answer = fields.Image(readonly=False)

    def _compute_name(self):
        for rec in self:
            if hasattr(rec.resource_ref, 'name'):
                rec.name = f'{rec.image_id.name} - {rec.resource_ref.name}'
            elif hasattr(rec.resource_ref, 'display_name'):
                rec.name = f'{rec.image_id.name} - {rec.resource_ref.display_name}'
            else:
                rec.name = f'{rec.image_id.name} - {rec.model_id.name} ({self.res_id})'
