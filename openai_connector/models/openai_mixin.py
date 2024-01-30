# -*- coding: utf-8 -*-
# Copyright (C) 2022 - Michel Perrocheau (https://github.com/myrrkel).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval
from odoo.addons.base.models.ir_model import SAFE_EVAL_BASE
from odoo.tools import html2plaintext
import logging
from openai import OpenAI

_logger = logging.getLogger(__name__)


class OpenAiMixin(models.AbstractModel):
    _name = 'openai.mixin'
    _description = 'OpenAI Mixin'
    _inherit = ['mail.render.mixin']

    name = fields.Char()
    active = fields.Boolean(default=True)
    model_id = fields.Many2one('ir.model', string='Model', required=True, ondelete='cascade')
    domain = fields.Char()
    save_on_target_field = fields.Boolean()
    target_field_id = fields.Many2one('ir.model.fields', string='Target Field')
    prompt_template = fields.Text()
    prompt_template_id = fields.Many2one('ir.ui.view', string='Prompt Template View')
    n = fields.Integer(default=1)
    answer_lang_id = fields.Many2one('res.lang', string='Answer Language', context={'active_test': False})
    test_prompt = fields.Text(readonly=True)

    @api.model
    def get_openai(self):
        api_key = self.env['ir.config_parameter'].sudo().get_param('openai_api_key')
        if not api_key:
            raise UserError(_('OpenAI API key is required.'))
        client = OpenAI(api_key=api_key)
        return client

    def get_prompt(self, rec_id=0):
        context = {'html2plaintext': html2plaintext}
        lang = self.env.lang
        answer_lang_id = self.answer_lang_id or self.env['res.lang']._lang_get(lang)
        if answer_lang_id:
            context['answer_lang'] = answer_lang_id.name
        if self.prompt_template_id:
            prompt = self._render_template_qweb_view(self.prompt_template_id.xml_id, self.model_id.model, [rec_id],
                                                     add_context=context)
        elif self.prompt_template:
            prompt = self._render_template_qweb(self.prompt_template, self.model_id.model, [rec_id],
                                                add_context=context)
        else:
            raise UserError(_('A prompt template is required'))

        return prompt[rec_id].strip()

    def get_records(self, limit=0):
        domain = safe_eval(self.domain, SAFE_EVAL_BASE, {'self': self}) if self.domain else []
        rec_ids = self.env[self.model_id.model].search(domain, limit=limit)
        return rec_ids

    def get_record(self, rec_id):
        record_id = self.env[self.model_id.model].browse(rec_id)
        return record_id

    def run(self):
        for rec_id in self.get_records():
            self.apply(rec_id.id)

    def apply(self, rec_id, method=False):
        result_ids = self.openai_create(rec_id, method)
        for result_id in result_ids:
            if self.save_on_target_field:
                result_id.save_result_on_target_field()

    def openai_create(self, rec_id, method=False):
        return False

    def run_test_prompt(self):
        rec_id = self.get_records(limit=1).id
        if not rec_id:
            return
        self.test_prompt = self.get_prompt(rec_id)
