# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockValuationLayer(models.Model):
    _inherit = 'stock.valuation.layer'

    note = fields.Char(string="Notas", related='stock_move_id.origin')
    