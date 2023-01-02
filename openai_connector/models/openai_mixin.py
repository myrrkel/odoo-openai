# -*- coding: utf-8 -*-
# Copyright (C) 2022 - Myrrkel (https://github.com/myrrkel).
# License GPL-3.0 or later (https://www.gnu.org/licenses/gpl.html).

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval
from odoo.addons.base.models.ir_model import SAFE_EVAL_BASE
from odoo.tools import html2plaintext
import logging
import openai

_logger = logging.getLogger(__name__)


class OpenAiMixin(models.AbstractModel):
    _name = 'openai.mixin'
    _description = 'OpenAI Mixin'
    _inherit = ['mail.render.mixin']

    name = fields.Char()
    active = fields.Boolean(default=True)
    model_id = fields.Many2one('ir.model', string='Model', required=True, ondelete='cascade')
    domain = fields.Char()
    target_field_id = fields.Many2one('ir.model.fields', string='Target Field')
    prompt_template = fields.Text()
    n = fields.Integer(default=1)
    answer_lang_id = fields.Many2one('res.lang', string='Answer Language', context={'active_test': False})
    test_prompt = fields.Text(readonly=True)

    def get_openai(self):
        openai.api_key = self.env['ir.config_parameter'].sudo().get_param('openai_api_key')
        if not openai.api_key:
            raise UserError(_('OpenAI API key is required.'))
        return openai

    def get_prompt(self, rec_id):
        context = {'html2plaintext': html2plaintext}
        lang = self.env.lang
        answer_lang_id = self.answer_lang_id or self.env['res.lang']._lang_get(lang)
        if answer_lang_id:
            context['answer_lang'] = answer_lang_id.name
        prompt = self._render_template_qweb(self.prompt_template, self.model_id.model, [rec_id],
                                            add_context=context)
        return prompt[rec_id]

    def get_records(self, limit=0):
        domain = safe_eval(self.domain, SAFE_EVAL_BASE, {'self': self}) if self.domain else []
        rec_ids = self.env[self.model_id.model].search(domain, limit=limit)
        return rec_ids

    def run_test_prompt(self):
        rec_id = self.get_records(limit=1).id
        if not rec_id:
            return
        self.test_prompt = self.get_prompt(rec_id)

    def save_result_on_target_field(self, rec_id, result):
        record = self.env[self.model_id.model].browse(rec_id)
        record.write({self.target_field_id.name: result})