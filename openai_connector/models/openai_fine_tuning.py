# Copyright (C) 2024 - Michel Perrocheau (https://github.com/myrrkel).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import json
from tempfile import NamedTemporaryFile
from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
from odoo.addons.base.models.ir_model import SAFE_EVAL_BASE

import logging

_logger = logging.getLogger(__name__)


class OpenAiFineTuning(models.Model):
    _name = 'openai.fine.tuning'
    _description = 'OpenAI Fine-Tuning'

    def _get_training_model_list(self):
        return [('gpt-3.5-turbo', 'gpt-3.5-turbo'),
                ('gpt-3.5-turbo-1106', 'gpt-3.5-turbo-1106'),
                ('gpt-3.5-turbo-0613', 'gpt-3.5-turbo-0613'),
                ('gpt-4-0613', 'gpt-4-0613'),
                ('babbage-002', 'babbage-002'),
                ('davinci-002', 'davinci-002')]

    name = fields.Char()
    training_model = fields.Selection(selection=_get_training_model_list, default='gpt-3.5-turbo')
    training_file_id = fields.Char('Training File ID')
    fine_tuning_job_id = fields.Char('Fine-Tuning Job ID')
    fine_tuned_model = fields.Char('Fine-Tuned Model')
    question_answer_domain = fields.Char()
    question_answer_ids = fields.Many2many('openai.question.answer', string='Questions /Answers',
                                           compute='_compute_question_answers',
                                           store=False)
    system_role_content = fields.Char()

    def _compute_question_answers(self):
        for rec in self:
            domain = safe_eval(rec.question_answer_domain,
                               SAFE_EVAL_BASE,
                               {'self': rec}) if rec.question_answer_domain else []
            rec.question_answer_ids = self.env['openai.question.answer'].search(domain)

    def get_training_content(self):
        content = ''
        for question_answer_id in self.question_answer_ids:
            messages = {
                'messages': [
                    {'role': 'system', 'content': self.system_role_content},
                    {'role': 'user', 'content': question_answer_id.name},
                    {'role': 'assistant', 'content': question_answer_id.answer}
                ]
            }
            content += json.dumps(messages) + '\n'
        return bytes(content, 'utf-8')

    def create_training_file(self):
        client = self.env['openai.mixin'].get_openai()
        file = ('training_%s' % self.id, self.get_training_content())
        res = client.files.create(file=file, purpose='fine-tune')
        self.training_file_id = res.id

    def create_fine_tuning(self):
        client = self.env['openai.mixin'].get_openai()
        res = client.fine_tuning.jobs.create(training_file=self.training_file_id, model=self.training_model)
        self.fine_tuning_job_id = res.id
        _logger.info(res)

    def update_fine_tuned_model(self):
        client = self.env['openai.mixin'].get_openai()
        res = client.fine_tuning.jobs.retrieve(self.fine_tuning_job_id)
        self.fine_tuned_model = res.fine_tuned_model
        _logger.info(res)

    def action_create_training_file(self):
        for rec in self:
            rec.create_training_file()

    def action_create_fine_tuning(self):
        for rec in self:
            rec.create_fine_tuning()

    def action_update_fine_tuned_model(self):
        for rec in self:
            rec.update_fine_tuned_model()
