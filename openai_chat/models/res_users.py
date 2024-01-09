# -*- coding: utf-8 -*-
# Copyright (C) 2023 - Michel Perrocheau (https://github.com/myrrkel).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    def _init_messaging(self):
        if self._is_internal():
            self._init_ai_bot()
        return super()._init_messaging()

    def _init_ai_bot(self):
        self.ensure_one()
        ai_bot_partner_id = self.env['ir.model.data']._xmlid_to_res_id('openai_chat.partner_ai')
        channel_info = self.env['mail.channel'].channel_get([ai_bot_partner_id, self.partner_id.id])
        channel = self.env['mail.channel'].browse(channel_info['id'])
        return channel
