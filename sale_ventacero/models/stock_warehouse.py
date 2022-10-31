# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    entrega_turnos = fields.Boolean(string="Entrega con turnos")
    