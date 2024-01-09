# -*- coding: utf-8 -*-
# Copyright (C) 2023 - Michel Perrocheau (https://github.com/myrrkel).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def action_openai_create_product_sales_description(self):
        completion_id = self.env.ref('openai_product_description.completion_product_description')
        for rec in self:
            completion_id.apply(rec.id)
        action_name = 'openai_product_description.openai_product_description_result_action'
        action = self.env['ir.actions.act_window']._for_xml_id(action_name)
        action['domain'] = [('res_id', 'in', self.ids)]
        return action
