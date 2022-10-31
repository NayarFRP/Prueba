# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockLocation(models.Model):
    _inherit = 'stock.location'

    allowed_users = fields.Many2many('res.users', string="Usuarios permitidos")
