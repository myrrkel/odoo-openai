/** @odoo-module **/

import { registerPatch } from '@mail/model/model_core';
import { insert } from '@mail/model/model_field_command';

registerPatch({
    name: 'MessagingInitializer',
    recordMethods: {
        /**
         * @override
         */
        _initCommands() {
            this._super();
            this.messaging.update({
                commands: insert({
                    help: this.env._t("Clear chat with AI Bot"),
                    methodName: 'execute_command_clear_ai_chat',
                    name: "clear",
                }),
            });
        },
    },
});
