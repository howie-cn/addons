# -*- coding: utf-8 -*-

from odoo.addons.web.controllers import main
from odoo.addons.web.controllers.main import fix_view_modes


def clean_action(action):
    action.setdefault('flags', {})

    import ast
    context_dict = ast.literal_eval(action.get('context'))
    if 'import_enabled' in context_dict:
        action['flags'].update({'import_enabled': context_dict.get('import_enabled')})

    action_type = action.setdefault('type', 'ir.actions.act_window_close')
    if action_type == 'ir.actions.act_window':
        return fix_view_modes(action)
    return action


main.clean_action = clean_action
