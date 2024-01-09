# -*- coding: utf-8 -*-
# Copyright (C) 2023 - Michel Perrocheau (https://github.com/myrrkel).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, _


class MailChannel(models.Model):
    _inherit = 'mail.channel'

    def execute_command_clear_ai_chat(self, **kwargs):
        partner = self.env.user.partner_id
        key = kwargs['body']
        if key.lower().strip() == '/clear':
            ai_bot_id = self.env['ir.model.data']._xmlid_to_res_id('openai_chat.partner_ai')
            ai_chat_member_ids = {ai_bot_id, partner.id}
            if ai_chat_member_ids == set(self.channel_member_ids.mapped('partner_id.id')):
                self.env['bus.bus']._sendone(self.env.user.partner_id, 'mail.message/delete',
                                             {'message_ids': self.message_ids.ids})
                self.message_ids.unlink()
