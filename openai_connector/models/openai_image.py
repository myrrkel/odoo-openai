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
        # res = self.run_image_method(prompt)
        # image_url = res['data'][0]['url']
        image_url = 'https://oaidalleapiprodscus.blob.core.windows.net/private/org-bnQHvSqiGxNzSx39MYTbr2xi/user-l2oXR7Xbf4kmIXFvNwxtXoKO/img-I5SGYmzf8XPCbuiQA8Cb2Gem.png?st=2022-12-31T11%3A29%3A26Z&se=2022-12-31T13%3A29%3A26Z&sp=r&sv=2021-08-06&sr=b&rscd=inline&rsct=image/png&skoid=6aaadede-4fb3-4698-a8f6-684d7786b067&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2022-12-31T04%3A07%3A01Z&ske=2023-01-01T04%3A07%3A01Z&sks=b&skv=2021-08-06&sig=yIA%2B%2BJLnwGETFKPyFiPv0BRyQO2Uumh1NYqkPH/2J5M%3D'
        result_id = self.create_result(rec_id, prompt, image_url)
        return result_id

    def run_image_method(self, prompt):
        openai = self.get_openai()
        if self.method == 'create':
            return openai.Image.create(prompt=prompt, n=self.n)
        if self.method == 'create_edit':
            return openai.Image.create_edit(prompt=prompt, n=self.n)
        if self.method == 'create_variation':
            return openai.Image.create_variation(prompt=prompt, n=self.n)

    def apply_image(self, rec_id):
        result_id = self.create_image(rec_id)
        self.save_result_on_target_field(rec_id, result_id.answer)

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

    def run_image(self):
        for rec_id in self.get_records():
            self.apply_image(rec_id.id)

    def run_test_image(self):
        rec_id = self.get_records(limit=1).id
        if not rec_id:
            return
        self.test_prompt = self.get_prompt(rec_id)
        result_id = self.create_image(rec_id)
        self.test_answer = result_id.answer
