# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    allowed_users = fields.Many2many('res.users', string="Usuarios permitidos")
