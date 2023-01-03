# -*- coding: utf-8 -*-
# Copyright (C) 2022 - Myrrkel (https://github.com/myrrkel).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class OpenAiEditResult(models.Model):
    _name = 'openai.edit.result'
    _description = 'OpenAI Edit Result'
    _inherit = ['openai.result.mixin']

    edit_id = fields.Many2one('openai.edit', string='Edit', readonly=True, ondelete='cascade')
    answer = fields.Text(readonly=False)
    input = fields.Text(readonly=False)
    origin_answer = fields.Text(readonly=True)
    prompt_tokens = fields.Integer(readonly=True)
    completion_tokens = fields.Integer(readonly=True)
    total_tokens = fields.Integer(readonly=True)

    def _compute_name(self):
        for rec in self:
            if hasattr(rec.resource_ref, 'name'):
                rec.name = f'{rec.edit_id.name} - {rec.resource_ref.name}'
            elif hasattr(rec.resource_ref, 'display_name'):
                rec.name = f'{rec.edit_id.name} - {rec.resource_ref.display_name}'
            else:
                rec.name = f'{rec.edit_id.name} - {rec.model_id.name} ({rec.res_id})'

    def write(self, vals):
        if self.answer and vals.get('answer'):
            vals['origin_answer'] = self.answer
        return super(OpenAiEditResult, self).write(vals)


