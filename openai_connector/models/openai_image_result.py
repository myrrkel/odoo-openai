# -*- coding: utf-8 -*-
# Copyright (C) 2022 - Michel Perrocheau (https://github.com/myrrkel).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class OpenAiImageResult(models.Model):
    _name = 'openai.image.result'
    _description = 'OpenAI Image Result'
    _inherit = ['openai.result.mixin']

    image_id = fields.Many2one('openai.image', string='OpenAI Action', readonly=True, ondelete='cascade')
    original_image = fields.Image(compute='_compute_original_image')
    method = fields.Char()
    answer = fields.Image(readonly=False)

    def _compute_name(self):
        for rec in self:
            if hasattr(rec.resource_ref, 'name'):
                name = f'{rec.image_id.name} - {rec.resource_ref.name}'
            elif hasattr(rec.resource_ref, 'display_name'):
                name = f'{rec.image_id.name} - {rec.resource_ref.display_name}'
            else:
                name = f'{rec.image_id.name} - {rec.model_id.name} ({self.res_id})'
            if rec.test_result:
                name = '%s (%s)' % (name, _('TEST'))
            rec.name = name

    def _compute_original_image(self):
        for rec in self:
            try:
                record_id = self.env[rec.model_id.model].browse(rec.res_id)
                if rec.image_id.source_image_field_id:
                    res = record_id[rec.image_id.source_image_field_id.name]
                    if res:
                        rec.original_image = res
                        continue
                rec.original_image = None
            except Exception as err:
                _logger.error(err)
                pass
