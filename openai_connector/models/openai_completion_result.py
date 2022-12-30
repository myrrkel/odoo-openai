# -*- coding: utf-8 -*-
# Copyright (C) 2022 - Myrrkel (https://github.com/myrrkel).
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class OpenAiCompletionResult(models.Model):
    _name = 'openai.completion.result'
    _description = 'OpenAI Completion Result'

    name = fields.Char(compute='_compute_name')
    completion_id = fields.Many2one('openai.completion', string='Completion', readonly=True, ondelete='cascade')
    model_id = fields.Many2one('ir.model', string='Model', readonly=True, ondelete='cascade')
    model = fields.Char(related='model_id.model', string='Model Name', readonly=True, store=True)
    target_field_id = fields.Many2one('ir.model.fields', string='Target Field', readonly=True)
    res_id = fields.Integer('Resource ID', readonly=True)
    resource_ref = fields.Reference(string='Record', selection='_selection_target_model',
                                    compute='_compute_resource_ref', inverse='_set_resource_ref', readonly=True)
    prompt = fields.Text(readonly=True)
    answer = fields.Text(readonly=False)
    origin_answer = fields.Text(readonly=True)
    prompt_tokens = fields.Integer(readonly=True)
    completion_tokens = fields.Integer(readonly=True)
    total_tokens = fields.Integer(readonly=True)

    def _compute_display_name(self):
        for rec in self:
            if hasattr(self.resource_ref, 'name'):
                rec.display_name = f'{self.completion_id.name} - {self.resource_ref.name}'
            elif hasattr(self.resource_ref, 'display_name'):
                rec.display_name = f'{self.completion_id.name} - {self.resource_ref.display_name}'
            else:
                rec.display_name = f'{self.completion_id.name} - {self.model_id.name} ({self.res_id})'

    @api.model
    def _selection_target_model(self):
        model_ids = self.env['ir.model'].search([])
        return [(model.model, model.name) for model in model_ids]

    @api.depends('model_id', 'res_id')
    def _compute_resource_ref(self):
        for rec in self:
            if rec.model_id and rec.res_id:
                record = self.env[rec.model_id.model].browse(rec.res_id)
                res_id = record[0] if record else 0
                rec.resource_ref = '%s,%s' % (rec.model_id.model, res_id.id)
            else:
                rec.resource_ref = False

    @api.onchange('resource_ref')
    def _set_resource_ref(self):
        for rec in self:
            rec.res_id = rec.resource_ref.id

    def write(self, vals):
        if self.answer and vals.get('answer'):
            vals['origin_answer'] = self.answer
        return super(OpenAiCompletionResult, self).write(vals)

    def apply_completion(self):
        self.resource_ref.write({self.target_field_id.name: self.answer})
