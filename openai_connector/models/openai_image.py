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


def resize_image(image, size, origin_x, origin_y):
    res_image = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    res_image.paste(image, (int((size - origin_x) / 2), int((size - origin_y) / 2)))
    return res_image


def square_image(binary_image, ratio=1):
    res_image = Image.open(io.BytesIO(base64.b64decode(binary_image)))
    x, y = res_image.size
    size = max(x, y)
    res_image = resize_image(res_image, size, x, y)

    if ratio not in [0, 1]:
        zoom_size = int(size * 1 / ratio)
        res_image = resize_image(res_image, zoom_size, size, size)

    img_byte_arr = io.BytesIO()
    res_image.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()


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
    size = fields.Selection(selection='_get_openai_image_size_list', default='1024x1024')
    source_image_field_id = fields.Many2one('ir.model.fields', string='Source Image Field')
    mask_image_field_id = fields.Many2one('ir.model.fields', string='Mask Image Field')
    resize_ratio_field_id = fields.Many2one('ir.model.fields', string='Resize Ratio Field')
    test_answer = fields.Image(readonly=True)
    test_source_image = fields.Image()
    test_mask_image = fields.Image()
    test_resize_ratio = fields.Float(default=1)

    def create_image(self, rec_id, method=False):
        prompt = self.get_prompt(rec_id)
        res = self.run_image_method(prompt, rec_id, method)
        if not res:
            return
        if isinstance(res, bytes):
            return self.create_result(rec_id, prompt, res)
        result_ids = []
        for data in res['data']:
            if data.get('b64_json'):
                result_id = self.create_result(rec_id, prompt, data.get('b64_json'), method=method)
            else:
                result_id = self.create_result_from_url(rec_id, prompt, data['url'], method=method)
            result_ids.append(result_id)
        return result_ids

    def get_source_image(self, rec_id, resize=False):
        record_id = self.get_record(rec_id)
        if self.env.context.get('openai_test') and self.test_source_image:
            return square_image(self.test_source_image, self.test_resize_ratio or 1)

        image_field = self.source_image_field_id.name or self.target_field_id.name
        if not image_field:
            return
        image = record_id[image_field]
        if not image and self.source_image_field_id.name:
            image = record_id[self.target_field_id.name]
        if image:
            return square_image(image, self.get_image_ratio(rec_id) if resize else 1)

    def get_mask_image(self, rec_id):
        record_id = self.get_record(rec_id)
        if self.env.context.get('openai_test') and self.test_mask_image:
            return square_image(self.test_mask_image, self.test_resize_ratio or 1)

        if self.mask_image_field_id:
            mask = record_id[self.mask_image_field_id.name]
            if mask:
                return square_image(mask, self.get_image_ratio(rec_id))
        return None

    def get_image_ratio(self, rec_id):
        record_id = self.get_record(rec_id)
        if self.resize_ratio_field_id:
            return record_id[self.resize_ratio_field_id.name] or 1
        return 1

    def run_image_method(self, prompt, rec_id=False, method=False):
        openai = self.get_openai()
        method = method or self.method
        if self.env.context.get('openai_test'):
            number_of_result = 1
        else:
            number_of_result = self.n or 1

        if method == 'create':
            return openai.Image.create(prompt=prompt,
                                       n=number_of_result,
                                       size=self.size or '1024x1024',
                                       response_format='b64_json')
        if method == 'create_edit':
            image = self.get_source_image(rec_id, resize=True)
            if not image:
                return
            mask = self.get_mask_image(rec_id)

            return openai.Image.create_edit(prompt=prompt,
                                            image=image,
                                            mask=mask,
                                            n=number_of_result,
                                            size=self.size,
                                            response_format='b64_json')
        if method == 'create_variation':
            image = self.get_source_image(rec_id)
            if not image:
                return
            return openai.Image.create_variation(image=image,
                                                 n=number_of_result,
                                                 size=self.size,
                                                 response_format='b64_json')

    def openai_create(self, rec_id, method=False):
        return self.create_image(rec_id, method=method)

    def create_result_from_url(self, rec_id, prompt, image_url):
        return self.create_result(rec_id, prompt, base64.b64encode(requests.get(image_url).content))

    def create_result(self, rec_id, prompt, answer, method=False):
        values = {'image_id': self.id,
                  'model_id': self.model_id.id,
                  'target_field_id': self.target_field_id.id,
                  'res_id': rec_id,
                  'prompt': prompt,
                  'answer': answer,
                  'method': method,
                  'test_result': self.env.context.get('openai_test', False),
                  }
        result_id = self.env['openai.image.result'].create(values)
        return result_id

    def run_test_image(self):
        rec_id = self.get_records(limit=1).id
        if not rec_id:
            return
        self.test_prompt = self.get_prompt(rec_id)
        result_ids = self.with_context(openai_test=True).create_image(rec_id)
        if result_ids:
            self.test_answer = result_ids[0].answer
            return {'type': 'ir.actions.client', 'tag': 'reload'}

    def result_to_source_image(self):
        self.test_source_image = self.test_answer
