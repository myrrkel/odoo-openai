# -*- coding: utf-8 -*-
# Copyright (C) 2022 - Myrrkel (https://github.com/myrrkel).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
import base64
import logging
import requests
import io
from PIL import Image

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
    source_image_field_id = fields.Many2one('ir.model.fields', string='Source Image Field')
    mask_image_field_id = fields.Many2one('ir.model.fields', string='Mask Image Field')
    resize_ratio_field_id = fields.Many2one('ir.model.fields', string='Resize Ratio Field')
    test_answer = fields.Image(readonly=True)

    def create_image(self, rec_id):
        prompt = self.get_prompt(rec_id)
        res = self.run_image_method(prompt, rec_id)
        if isinstance(res, bytes):
            return self.create_result(rec_id, prompt, res)
        result_ids = []
        for data in res['data']:
            if data.get('b64_json'):
                result_id = self.create_result(rec_id, prompt, data.get('b64_json'))
            else:
                result_id = self.create_result_from_url(rec_id, prompt, data['url'])
            result_ids.append(result_id)
        return result_ids

    def get_source_image(self, rec_id):
        record_id = self.get_record(rec_id)
        if self.source_image_field_id:
            image = record_id[self.source_image_field_id.name]
            if image:
                return self.square_image(image, self.get_image_ratio(rec_id))

    def get_mask_image(self, rec_id):
        record_id = self.get_record(rec_id)
        if self.mask_image_field_id:
            mask = record_id[self.mask_image_field_id.name]
            if mask:
                return self.square_image(mask, self.get_image_ratio(rec_id))
        return None

    def get_image_ratio(self, rec_id):
        record_id = self.get_record(rec_id)
        if self.resize_ratio_field_id:
            return record_id[self.resize_ratio_field_id.name] or 1
        return 1

    def run_image_method(self, prompt, rec_id=False):
        openai = self.get_openai()
        if self.method == 'create':
            return openai.Image.create(prompt=prompt, n=self.n, response_format='b64_json')
        if self.method == 'create_edit':
            image = self.get_source_image(rec_id)
            if not image:
                return

            mask = self.get_mask_image(rec_id)

            return openai.Image.create_edit(prompt=prompt,
                                            image=image,
                                            mask=mask,
                                            n=self.n,
                                            response_format='b64_json')
        if self.method == 'create_variation':
            return openai.Image.create_variation(prompt=prompt, n=self.n, response_format='b64_json')

    def square_image(self, binary_image, ratio=1):
        image = Image.open(io.BytesIO(base64.b64decode(binary_image)))
        x, y = image.size
        size = max(x, y)
        zoom_size = int(size*1/ratio)
        new_image = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        new_image.paste(image, (int((size - x) / 2), int((size - y) / 2)))

        res_image = Image.new('RGBA', (zoom_size, zoom_size), (255, 255, 255, 0))
        res_image.paste(new_image, (int((zoom_size - size) / 2), int((zoom_size - size) / 2)))

        img_byte_arr = io.BytesIO()
        res_image.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()

    def openai_create(self, rec_id):
        return self.create_image(rec_id)

    def create_result_from_url(self, rec_id, prompt, image_url):
        return self.create_result(rec_id, prompt, base64.b64encode(requests.get(image_url).content))

    def create_result(self, rec_id, prompt, answer):
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
