# -*- coding: utf-8 -*-
# Copyright (C) 2022 - Myrrkel (https://github.com/myrrkel).
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
from odoo.addons.base.models.ir_model import SAFE_EVAL_BASE
from odoo.tools import html2plaintext

import logging

_logger = logging.getLogger(__name__)


class OpenAiCompletion(models.Model):
    _name = 'openai.completion'
    _description = 'OpenAI Completion'
    _inherit = ['openai.mixin', 'mail.render.mixin']

    def _get_openai_model_list(self):
        openai = self.get_openai()
        model_list = openai.Model.list()
        res = [(m.id, m.id) for m in model_list.data]
        res.sort()
        return res

    name = fields.Char()
    active = fields.Boolean(default=True)
    model_id = fields.Many2one('ir.model', string='Model', required=True, ondelete='cascade')
    domain = fields.Char()
    target_field_id = fields.Many2one('ir.model.fields', string='Target Field')
    prompt_template = fields.Text()
    ai_model = fields.Selection(selection='_get_openai_model_list', string='AI Model', required=True)
    answer_lang_id = fields.Many2one('res.lang', string='Answer Language', context={'active_test': False})
    temperature = fields.Float(default=1)
    max_tokens = fields.Integer(default=16)
    top_p = fields.Float(default=1)
    frequency_penalty = fields.Float()
    presence_penalty = fields.Float()
    test_prompt = fields.Text(readonly=True)
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

    def get_prompt(self, rec_id):
        context = {'html2plaintext': html2plaintext}
        lang = self.env.lang
        answer_lang_id = self.answer_lang_id or self.env['res.lang']._lang_get(lang)
        if answer_lang_id:
            context['answer_lang'] = answer_lang_id.name
        prompt = self._render_template_qweb(self.prompt_template, self.model_id.model, [rec_id],
                                            add_context=context)
        return prompt[rec_id]

    def apply_completion(self, rec_id):
        result_id = self.create_completion(rec_id)

        record = self.env[self.model_id.model].browse(rec_id)
        record.write({self.target_field_id.name: result_id.answer})

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

    def get_records(self, limit=0):
        domain = safe_eval(self.domain, SAFE_EVAL_BASE, {'self': self}) if self.domain else []
        rec_ids = self.env[self.model_id.model].search(domain, limit=limit)
        return rec_ids

    def run_completion(self):
        for rec_id in self.get_records():
            self.apply_completion(rec_id.id)

    def run_test_prompt(self):
        rec_id = self.get_records(limit=1).id
        if not rec_id:
            return
        self.test_prompt = self.get_prompt(rec_id)

    def run_test_completion(self):
        rec_id = self.get_records(limit=1).id
        if not rec_id:
            return
        self.test_prompt = self.get_prompt(rec_id)
        res = self.create_completion(rec_id)
        self.test_answer = res.choices[0].text
