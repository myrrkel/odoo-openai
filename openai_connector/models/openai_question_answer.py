# -*- coding: utf-8 -*-
# Copyright (C) 2024 - Michel Perrocheau (https://github.com/myrrkel).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _

import logging

_logger = logging.getLogger(__name__)


class OpenAiQuestionAnswer(models.Model):
    _name = 'openai.question.answer'
    _description = 'OpenAI Question Answer'

    name = fields.Text('Question')
    answer = fields.Text('Answer')
    model_id = fields.Many2one('ir.model', string='Model', ondelete='cascade')
    model = fields.Char(related='model_id.model', string='Model Name', readonly=True, store=True)
    res_id = fields.Integer('Resource ID', readonly=True)
    resource_ref = fields.Reference(string='Record', selection='_selection_target_model',
                                    compute='_compute_resource_ref', inverse='_set_resource_ref')
    answer_completion_id = fields.Many2one('openai.completion', string='Answer Completion')
    content_length = fields.Integer(compute='_compute_content_length')

    @api.model
    def _selection_target_model(self):
        model_ids = self.env['ir.model'].search([])
        return [(model.model, model.name) for model in model_ids]

    def _compute_content_length(self):
        for res in self:
            res.content_length = len(res.name) + len(res.answer)

    @api.depends('res_id')
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
            if rec.resource_ref:
                rec.model_id = self.env['ir.model']._get(rec.resource_ref._name)
                rec.res_id = rec.resource_ref.id

    def action_answer_question(self):
        for rec in self:
            res = rec.answer_completion_id.create_completion(rec.id)
            rec.answer = res[0].answer

    def get_score(self, keyword_list):
        score = 0
        for keyword in keyword_list:
            keyword = keyword.lower()
            if keyword in self.name.lower():
                score += 2
            if keyword in self.answer.lower():
                score += 1
        return score
