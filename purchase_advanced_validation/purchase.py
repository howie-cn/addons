# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2016-2016 jeffery (<jeffery9@gmail.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

from openerp import models, fields, api
from openerp.tools.translate import _


class purchase(models.Model):
    _inherit = "purchase.order"

    technical = fields.Boolean(
        string='Technical',
        default=False,
    )

    case_type = fields.Selection(
        string='Case Type',
        default='other',
        selection=[('other','Other'),('technical', 'Technical'), ('production', 'Production')]
    )

    state = fields.Selection(selection_add=[('validated', "Validated")])