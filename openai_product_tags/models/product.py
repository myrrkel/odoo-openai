# -*- coding: utf-8 -*-
# Copyright (C) 2023 - Michel Perrocheau (https://github.com/myrrkel).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def action_openai_create_product_tags(self):
        completion_id = self.env.ref('openai_product_tags.completion_product_tags')
        for rec in self:
            completion_id.apply(rec.id)
        if not completion_id.save_on_target_field:
            action_name = 'openai_product_tags.openai_product_tags_result_action'
            action = self.env['ir.actions.act_window']._for_xml_id(action_name)
            action['domain'] = [('res_id', 'in', self.ids)]
            return action
