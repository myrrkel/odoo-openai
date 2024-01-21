# -*- coding: utf-8 -*-
# Copyright (C) 2022 - Michel Perrocheau (https://github.com/myrrkel).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
import ast
import logging
import re

_logger = logging.getLogger(__name__)


def clean_list_element(el):
    if '.' in el:
        el = el.split('.')[1]
    if '-' in el:
        el = el.split('-')[1]
    el = re.sub(r'[^\w\s,-]', '', el.strip())
    return el


class OpenAiCompletionResult(models.Model):
    _name = 'openai.completion.result'
    _description = 'OpenAI Completion Result'
    _inherit = ['openai.result.mixin']

    completion_id = fields.Many2one('openai.completion', string='Completion', readonly=True, ondelete='cascade')
    answer = fields.Text(readonly=False)
    origin_answer = fields.Text(readonly=True)
    prompt_tokens = fields.Integer(readonly=True)
    completion_tokens = fields.Integer(readonly=True)
    total_tokens = fields.Integer(readonly=True)

    def _compute_name(self):
        for rec in self:
            if hasattr(rec.resource_ref, 'name'):
                rec.name = f'{rec.completion_id.name} - {rec.resource_ref.name}'
            elif hasattr(rec.resource_ref, 'display_name'):
                rec.name = f'{rec.completion_id.name} - {rec.resource_ref.display_name}'
            else:
                rec.name = f'{rec.completion_id.name} - {rec.model_id.name} ({rec.res_id})'

    def write(self, vals):
        if self.answer and vals.get('answer') and not self.origin_answer:
            vals['origin_answer'] = self.answer
        return super(OpenAiCompletionResult, self).write(vals)

    def exec_post_process(self, value):
        if not self.completion_id.post_process:
            return value
        post_process_function = getattr(self, self.completion_id.post_process)
        return post_process_function(value)

    def get_answer_value(self):
        return self.exec_post_process(self.answer)

    def json_to_questions(self, val):
        values = ast.literal_eval(val)
        questions = values.get('questions', [])
        for question in questions:
            create_vals = {'name': question,
                           'model_id': self.model_id.id,
                           'res_id': self.res_id,
                           }
            self.env['openai.question.answer'].create(create_vals)

    def list_to_many2many(self, val):
        """
        :param val: a string representing a  python list or a comma separated list
        e.g: "test = ['val1', 'val2']" or " val1, val2, "
        :return: a many2many update list.
        e.g: [(5, 0, 0), (0, 0, {'name': 'new tag'})]
        """

        res = [(5, 0, 0)]
        if '=' in val:
            val = val.split('=')[1]
        val = val.strip()
        if val[0] == '[':
            # Eval Python list string
            val_list = ast.literal_eval(val)
        else:
            # Split the string
            if '\n' in val:
                separator = '\n'
            else:
                separator = ','
            val_list = val.split(separator)

        val_list = [clean_list_element(el) for el in val_list]
        if not val_list:
            return False

        # Create many2many update list
        target_model = self.target_field_id.relation
        for el in val_list:
            if not el:
                continue
            rec_el = self.env[target_model].search([('name', '=', el)])
            if not rec_el:
                res.append((0, 0, {'name': el}))
            else:
                res.append((4, rec_el.id))
        return res
