# -*- coding: utf-8 -*-
# Copyright (C) 2023 - Michel Perrocheau (https://github.com/myrrkel).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def _message_post_after_hook(self, message, msg_vals):
        res = super(MailThread, self)._message_post_after_hook(message, msg_vals)
        partner_ai = self.env.ref('openai_chat.partner_ai')
        if partner_ai in self.mapped('channel_member_ids.partner_id'):
            self.env['mail.ai.bot']._answer_to_message(self, msg_vals)
        return res
