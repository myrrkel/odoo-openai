# Copyright (C) 2024 - Michel Perrocheau (https://github.com/myrrkel).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import json
from odoo import models, fields, api, _
from odoo.osv import expression

import logging

_logger = logging.getLogger(__name__)


class OpenAiTool(models.Model):
    _name = 'openai.tool'
    _description = 'OpenAI Tool'

    def _get_tool_type_list(self):
        return [('function', _('Function'))]

    name = fields.Char()
    description = fields.Text()
    model_id = fields.Many2one('ir.model', string='Model', ondelete='cascade')
    model = fields.Char(related='model_id.model', string='Model Name', readonly=True, store=True)
    type = fields.Selection(selection=_get_tool_type_list)
    property_ids = fields.One2many('openai.tool.property', 'tool_id', copy=True)
    required_property_ids = fields.One2many('openai.tool.property', 'tool_id', readonly=True,
                                            domain=[('required', '=', True)])

    def get_tool_dict(self):
        res = {'type': 'function',
               'function': {
                   'name': self.name,
                   'description': self.description}}
        properties = {}
        for property_id in self.property_ids:
            properties[property_id.name] = {'type': property_id.type,
                                            'description': property_id.description}
        if properties:
            parameters = {'type': 'object',
                          'properties': properties}
            required = [p.name for p in self.required_property_ids]
            if required:
                parameters['required'] = required
            res['function']['parameters'] = parameters
        return res

    @api.model
    def search_question_answer(self, keywords):
        if ',' not in keywords:
            keywords = keywords.replace(' ', ',')
        keyword_list = keywords.split(',')
        domain = []
        for keyword in keyword_list:
            domain = expression.OR([domain, [('name', '=ilike', f'%{keyword}%')]])
            domain = expression.OR([domain, [('answer', '=ilike', f'%{keyword}%')]])
        question_answer_ids = self.env['openai.question.answer'].search(domain)
        if not question_answer_ids:
            return 'No result found. Suggest to user to reformulate his question or to suggest some keywords.'
        res = [{'question': q.name,
                'answer': q.answer,
                'score': q.get_score(keyword_list),
                'length': q.content_length,
                }
               for q in question_answer_ids]
        res = sorted(res, key=lambda x: x['score'], reverse=True)
        max_score = res[0]['score']
        res = list(filter(lambda x: x['score'] == max_score, res))
        res = sorted(res, key=lambda x: x['length'])
        return json.dumps(res[0])

    @api.model
    def get_search_question_answer_tool(self):
        return {
            "type": "function",
            "function": {
                "name": "search_question_answer",
                "description": "Search by keywords in the frequently asked questions database. "
                               "Returns a list of questions with their answers",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "keywords": {
                            "type": "string",
                            "description": "A list of comma separated keywords. Example: keyword1,keyword2,keyword3",
                        },
                    },
                    "required": ["keywords"],
                },
            }
        }
