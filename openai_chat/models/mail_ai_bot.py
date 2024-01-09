# -*- coding: utf-8 -*-
# Copyright (C) 2023 - Michel Perrocheau (https://github.com/myrrkel).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, _
from odoo.tools import plaintext2html, html2plaintext
from odoo.exceptions import UserError
import logging
import openai

_logger = logging.getLogger(__name__)


class MailBot(models.AbstractModel):
    _name = 'mail.ai.bot'
    _description = 'Mail AI Bot'

    def _answer_to_message(self, record, values):
        ai_bot_id = self.env['ir.model.data']._xmlid_to_res_id('openai_chat.partner_ai')
        if len(record) != 1 or values.get('author_id') == ai_bot_id or values.get('message_type') != 'comment':
            return
        if self._is_bot_in_private_channel(record):
            if values.get('body', '').startswith('!'):
                answer_type = 'important'
            else:
                answer_type = 'chat'

            try:
                answer = self._get_answer(record, answer_type)
            except openai.APIError as err:
                _logger.error(err)
                if 'maximum context length' in err.message:
                    answer = _('ERROR - Sorry, this request requires too many tokens.'
                               'Please consider using the command "\\clean" to clear the AI chat.')
                    pass
                else:
                    raise UserError(err.message)

            if answer:
                message_type = 'comment'
                subtype_id = self.env['ir.model.data']._xmlid_to_res_id('mail.mt_comment')
                record = record.with_context(mail_create_nosubscribe=True).sudo()
                record.message_post(body=answer, author_id=ai_bot_id, message_type=message_type, subtype_id=subtype_id)

    def get_chat_messages(self, record, header, only_human=False):
        partner_ai_id = self.env.ref('openai_chat.partner_ai')
        previous_message_ids = record.message_ids.filtered(lambda m: m.body != '')
        if only_human:
            previous_message_ids = previous_message_ids.filtered(lambda m: m.author_id != partner_ai_id)

        chat_messages = [{'role': 'system', 'content': header}] if header else []
        for message_id in previous_message_ids.sorted('date'):
            role = 'assistant' if message_id.author_id == partner_ai_id else 'user'
            chat_message = {'role': role,
                            'content': html2plaintext(message_id.body)}
            chat_messages.append(chat_message)
        return chat_messages

    def _get_answer(self, record, answer_type='chat'):
        completion_id = self.env.ref('openai_chat.completion_chat')
        header = completion_id.prompt_template

        if answer_type == 'chat':
            messages = self.get_chat_messages(record, header)
            res = completion_id.create_completion(messages=messages)
        elif answer_type == 'important':
            messages = self.get_chat_messages(record, header, only_human=True)
            res = completion_id.create_completion(messages,
                                                  max_tokens=2048)
        else:
            return
        if res:
            return res[0]

    def _is_bot_in_private_channel(self, record):
        ai_bot_id = self.env['ir.model.data']._xmlid_to_res_id('openai_chat.partner_ai')
        if record._name == 'mail.channel' and record.channel_type == 'chat':
            return ai_bot_id in record.with_context(active_test=False).channel_partner_ids.ids
        return False
