# -*- coding: utf-8 -*-
# Copyright (C) 2022 - Myrrkel (https://github.com/myrrkel).
# License GPL-3.0 or later (https://www.gnu.org/licenses/gpl.html).

from odoo import models, fields, api, _

import logging

_logger = logging.getLogger(__name__)


class OpenAiCompletion(models.Model):
    _name = 'openai.completion'
    _description = 'OpenAI Completion'
    _inherit = ['openai.mixin']

    def _get_openai_model_list(self):
        openai = self.get_openai()
        model_list = openai.Model.list()
        res = [(m.id, m.id) for m in model_list.data]
        res.sort()
        return res

    ai_model = fields.Selection(selection='_get_openai_model_list', string='AI Model', required=True)
    temperature = fields.Float(default=1)
    max_tokens = fields.Integer(default=16)
    top_p = fields.Float(default=1)
    frequency_penalty = fields.Float()
    presence_penalty = fields.Float()
    test_answer = fields.Text(readonly=True)

    def create_completion(self, rec_id):
        openai = self.get_openai()
        prompt = self.get_prompt(rec_id)
        res = openai.Completion.create(
            model=self.ai_model,
            prompt=prompt,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            top_p=self.top_p,
            frequency_penalty=self.frequency_penalty,
            presence_penalty=self.presence_penalty,
        )
        answer = res.choices[0].text
        prompt_tokens = res.usage.prompt_tokens
        completion_tokens = res.usage.completion_tokens
        total_tokens = res.usage.total_tokens
        result_id = self.create_result(rec_id, prompt, answer, prompt_tokens, completion_tokens, total_tokens)
        return result_id

    def apply_completion(self, rec_id):
        result_id = self.create_completion(rec_id)
        self.save_result_on_target_field(rec_id, result_id.answer)

    def create_result(self, rec_id, prompt, answer, prompt_tokens, completion_tokens, total_tokens):
        values = {'completion_id': self.id,
                  'model_id': self.model_id.id,
                  'target_field_id': self.target_field_id.id,
                  'res_id': rec_id,
                  'prompt': prompt,
                  'answer': answer,
                  'prompt_tokens': prompt_tokens,
                  'completion_tokens': completion_tokens,
                  'total_tokens': total_tokens,
                  }
        result_id = self.env['openai.completion.result'].create(values)
        return result_id

    def run_completion(self):
        for rec_id in self.get_records():
            self.apply_completion(rec_id.id)

    def run_test_completion(self):
        rec_id = self.get_records(limit=1).id
        if not rec_id:
            return
        self.test_prompt = self.get_prompt(rec_id)
        res = self.create_completion(rec_id)
        self.test_answer = res.answer