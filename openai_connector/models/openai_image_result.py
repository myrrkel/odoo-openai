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
            if hasattr(self.resource_ref, 'name'):
                rec.name = f'{self.image_id.name} - {self.resource_ref.name}'
            elif hasattr(self.resource_ref, 'display_name'):
                rec.name = f'{self.image_id.name} - {self.resource_ref.display_name}'
            else:
                rec.name = f'{self.image_id.name} - {self.model_id.name} ({self.res_id})'

    def action_apply_image(self):
        self.image_id.save_result_on_target_field(self.res_id, self.answer)

