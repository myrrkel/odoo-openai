# -*- coding: utf-8 -*-
# Copyright (C) 2023 - Michel Perrocheau (https://github.com/myrrkel).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    openai_source_image = fields.Image("OpenAI Source Image", max_width=2000, max_height=2000)
    openai_mask_image = fields.Image("OpenAI Mask Image", max_width=2000, max_height=2000)
    image_ratio = fields.Float()
    image_description = fields.Char()

    def action_openai_create_product_edit_image(self):
        for rec in self:
            image_edit_id = self.env.ref('openai_edit_product_image.edit_product_image')
            if rec.openai_source_image:
                method = 'create_edit'
            elif rec.image_description:
                method = 'create'
            elif rec.image_1920:
                method = 'create_variation'
            else:
                continue
            image_edit_id.apply(rec.id, method=method)
        if image_edit_id.save_on_target_field:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': _("Product image created."),
                    'type': 'success',
                    'sticky': False,
                    'next': {'type': 'ir.actions.client', 'tag': 'reload'},
                }
            }
        else:
            action_name = 'openai_edit_product_image.openai_product_edit_image_action'
            action = self.env['ir.actions.act_window']._for_xml_id(action_name)
            action['domain'] = [('res_id', 'in', self.ids)]
            return action
