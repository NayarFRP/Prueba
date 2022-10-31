# -*- coding: utf-8 -*-
from odoo import models, api, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    team_id = fields.Many2one('crm.team', string='Sucursal')
    