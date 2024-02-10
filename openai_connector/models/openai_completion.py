# -*- coding: utf-8 -*-
# Copyright (C) 2022 - Michel Perrocheau (https://github.com/myrrkel).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import json

from odoo import models, fields, api, _

import logging

_logger = logging.getLogger(__name__)


class OpenAiCompletion(models.Model):
    _name = 'openai.completion'
    _description = 'OpenAI Completion'
    _inherit = ['openai.mixin']

    def _get_openai_model_list(self):
        try:
            openai = self.get_openai()
        except Exception as err:
            return [('gpt-3.5-turbo', 'gpt-3.5-turbo')]
        model_list = openai.models.list()
        res = [(m.id, m.id) for m in model_list.data]
        res.sort()
        return res

    def _get_post_process_list(self):
        return [('list_to_many2many', _('List to Many2many')),
                ('json_to_questions', _('JSON to questions'))]

    def _get_response_format_list(self):
        return [('text', _('Text')),
                ('json_object', _('JSON Object')),
                ]

    ai_model = fields.Selection(selection='_get_openai_model_list', string='AI Model')
    fine_tuning_id = fields.Many2one('openai.fine.tuning', string='Fine-Tuning')
    temperature = fields.Float(default=1)
    max_tokens = fields.Integer(default=3000)
    top_p = fields.Float(default=1)
    frequency_penalty = fields.Float()
    presence_penalty = fields.Float()
    stop = fields.Char()
    test_answer = fields.Text(readonly=True)
    post_process = fields.Selection(selection='_get_post_process_list')
    response_format = fields.Selection(selection='_get_response_format_list', default='text')
    tool_ids = fields.Many2many('openai.tool', string='Tools', copy=True)

    def create_completion(self, rec_id=0, messages=None, prompt='', **kwargs):
        openai = self.get_openai()
        if not messages:
            if not prompt:
                prompt = self.get_prompt(rec_id)
            messages = [{'role': 'user', 'content': prompt}]

        max_tokens = kwargs.get('max_tokens', self.max_tokens)
        stop = kwargs.get('stop', self.stop or '')
        if isinstance(stop, str) and ',' in stop:
            stop = stop.split(',')
        response_format = {'type': kwargs.get('response_format', self.response_format) or 'text'}
        model = self.ai_model or self.fine_tuning_id.fine_tuned_model or kwargs.get('model', 'gpt-3.5-turbo')
        temperature = self.temperature or kwargs.get('temperature', 0)
        top_p = self.top_p or kwargs.get('top_p', 0)
        max_tokens = kwargs.get('max_tokens', self.max_tokens or 3000)
        tools = [t.get_tool_dict() for t in self.tool_ids] if self.tool_ids else None
        _logger.info(f'Create completion: {messages}')
        res = openai.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            n=self.n or 1,
            temperature=temperature,
            top_p=top_p,
            frequency_penalty=self.frequency_penalty,
            presence_penalty=self.presence_penalty,
            stop=stop,
            response_format=response_format,
            tools=tools,
            tool_choice='auto' if tools else None,
        )
        prompt_tokens = res.usage.prompt_tokens
        completion_tokens = res.usage.completion_tokens
        total_tokens = res.usage.total_tokens

        result_ids = []
        for choice in res.choices:
            if choice.finish_reason == 'tool_calls':
                for tool_call in choice.message.tool_calls:
                    messages.append(choice.message)
                    messages.append(self.run_tool_call(tool_call))
                    return self.create_completion(rec_id, messages, prompt, **kwargs)
            _logger.info(f'Completion result: {choice.message.content}')
            if rec_id:
                answer = choice.message.content
                result_id = self.create_result(rec_id, prompt, answer, prompt_tokens, completion_tokens, total_tokens)
                if self.post_process and not self.target_field_id:
                    result_id.exec_post_process(answer)
                result_ids.append(result_id)
            else:
                return [choice.message.content for choice in res.choices]
        return result_ids

    def run_tool_call(self, tool_call):
        tool_name = tool_call.function.name
        res_dict = {'role': 'tool',
                    "tool_call_id": tool_call.id,
                    'content': '',
                    'name': tool_name}
        tool_id = self.tool_ids.filtered(lambda t: t.name == tool_name)
        if not tool_id:
            return res_dict
        model_name = tool_id.model or self.model_id.model
        model = self.env[model_name]

        if hasattr(model, tool_name):
            function = getattr(model, tool_name)
        else:
            model = self.env['openai.tool']
            if hasattr(model, tool_name):
                function = getattr(model, tool_name)
            else:
                return res_dict

        arguments = tool_call.function.arguments
        if arguments:
            arguments_vals = json.loads(arguments)
            _logger.info(f'Run tool: {tool_name}({arguments_vals})')
            res = function(**arguments_vals)
        else:
            res = function()
            _logger.info(f'Run tool: {tool_name}()')

        res_dict['content'] = str(res)
        return res_dict

    def openai_create(self, rec_id, method=False):
        return self.create_completion(rec_id)

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

    def run_test_completion(self):
        rec_id = self.get_records(limit=1).id
        if not rec_id:
            return
        self.test_prompt = self.get_prompt(rec_id)
        result_ids = self.create_completion(rec_id)
        self.test_answer = result_ids[0].answer
