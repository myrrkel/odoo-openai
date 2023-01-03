# -*- coding: utf-8 -*-
# Copyright (C) 2022 - Myrrkel (https://github.com/myrrkel).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
import base64
import logging
import requests

_logger = logging.getLogger(__name__)


class OpenAiImage(models.Model):
    _name = 'openai.image'
    _description = 'OpenAI Image'
    _inherit = ['openai.mixin']

    def _get_openai_image_size_list(self):
        size_list = ['256x256', '512x512', '1024x1024']
        res = [(m, m) for m in size_list]
        return res

    def _get_openai_image_method_list(self):
        return [
            ('create', _('Create')),
            ('create_edit', _('Edit')),
            ('create_variation', _('Variation')),
        ]

    method = fields.Selection(selection='_get_openai_image_method_list')
    size = fields.Selection(selection='_get_openai_image_size_list')
    test_answer = fields.Image(readonly=True)

    def create_image(self, rec_id):
        prompt = self.get_prompt(rec_id)
        res = self.run_image_method(prompt)
        result_ids = []
        for data in res['data']:
            image_url = data['url']
            result_id = self.create_result(rec_id, prompt, image_url)
            result_ids.append(result_id)
        return result_ids

    def run_image_method(self, prompt):
        openai = self.get_openai()
        if self.method == 'create':
            return openai.Image.create(prompt=prompt, n=self.n)
        if self.method == 'create_edit':
            return openai.Image.create_edit(prompt=prompt, n=self.n)
        if self.method == 'create_variation':
            return openai.Image.create_variation(prompt=prompt, n=self.n)

    def openai_create(self, rec_id):
        return self.create_image(rec_id)

    def create_result(self, rec_id, prompt, image_url):
        answer = base64.b64encode(requests.get(image_url).content)
        values = {'image_id': self.id,
                  'model_id': self.model_id.id,
                  'target_field_id': self.target_field_id.id,
                  'res_id': rec_id,
                  'prompt': prompt,
                  'answer': answer,
                  }
        result_id = self.env['openai.image.result'].create(values)
        return result_id

    def run_test_image(self):
        rec_id = self.get_records(limit=1).id
        if not rec_id:
            return
        self.test_prompt = self.get_prompt(rec_id)
        result_ids = self.create_image(rec_id)
        self.test_answer = result_ids[0].answer
