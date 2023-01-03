# -*- coding: utf-8 -*-
# Copyright (C) 2022 - Myrrkel (https://github.com/myrrkel).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _

import logging

_logger = logging.getLogger(__name__)


class OpenAiEdit(models.Model):
    _name = 'openai.edit'
    _description = 'OpenAI Edit'
    _inherit = ['openai.mixin']

    def _get_openai_edit_model_list(self):
        model_list = ['text-davinci-edit-001']
        res = [(m, m) for m in model_list]
        res.sort()
        return res

    ai_model = fields.Selection(selection='_get_openai_edit_model_list', string='AI Model', required=True)
    instruction = fields.Text()
    temperature = fields.Float(default=1)
    top_p = fields.Float(default=1)
    test_answer = fields.Text(readonly=True)

    def create_edit(self, rec_id):
        openai = self.get_openai()
        input_text = self.get_prompt(rec_id)
        res = openai.Edit.create(
            model=self.ai_model,
            input=input_text,
            instruction=self.instruction,
            n=self.n,
            temperature=self.temperature,
            top_p=self.top_p,
        )
        prompt_tokens = res.usage.prompt_tokens
        completion_tokens = res.usage.completion_tokens
        total_tokens = res.usage.total_tokens

        result_ids = []
        for choice in res.choices:
            answer = choice.text.strip()
            result_id = self.create_result(rec_id, input_text, answer, prompt_tokens, completion_tokens, total_tokens)
            result_ids.append(result_id)
        return result_ids


    def openai_create(self, rec_id):
        return self.create_edit(rec_id)

    def create_result(self, rec_id, prompt, input_text, answer, prompt_tokens, completion_tokens, total_tokens):
        values = {'edit_id': self.id,
                  'model_id': self.model_id.id,
                  'target_field_id': self.target_field_id.id,
                  'res_id': rec_id,
                  'prompt': prompt,
                  'input': input_text,
                  'answer': answer,
                  'prompt_tokens': prompt_tokens,
                  'completion_tokens': completion_tokens,
                  'total_tokens': total_tokens,
                  }
        result_id = self.env['openai.edit.result'].create(values)
        return result_id

    def run_test_edit(self):
        rec_id = self.get_records(limit=1).id
        if not rec_id:
            return
        self.test_prompt = self.get_prompt(rec_id)
        result_ids = self.create_edit(rec_id)
        self.test_answer = result_ids[0].answer
