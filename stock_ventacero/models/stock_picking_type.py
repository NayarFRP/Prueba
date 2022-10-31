# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    allowed_users = fields.Many2many('res.users', string="Usuarios permitidos")
    internal_transfer = fields.Boolean(string="Transferencia entre sucursales")
    