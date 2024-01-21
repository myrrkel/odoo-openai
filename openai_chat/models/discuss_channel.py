# -*- coding: utf-8 -*-
# Copyright (C) 2023 - Michel Perrocheau (https://github.com/myrrkel).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, _


class Channel(models.Model):
    _inherit = 'discuss.channel'

    ai_bot_partner_id = fields.Many2one('res.partner', 'AI Bot', compute='_compute_ai_bot_partner', store=False)

    def _compute_ai_bot_partner(self):
        for rec in self:
            rec.ai_bot_partner_id = rec.mapped('channel_member_ids.partner_id').filtered('is_ai_bot')

    def execute_command_clear_ai_chat(self, **kwargs):
        partner = self.env.user.partner_id
        key = kwargs['body']
        if key.lower().strip() == '/clear':
            if self.ai_bot_partner_id:
                ai_chat_member_ids = {self.ai_bot_partner_id.id, partner.id}
                if ai_chat_member_ids == set(self.mapped('channel_member_ids.partner_id.id')):
                    self.env['bus.bus']._sendone(self.env.user.partner_id, 'mail.message/delete',
                                                 {'message_ids': self.message_ids.ids})
                    self.message_ids.unlink()
