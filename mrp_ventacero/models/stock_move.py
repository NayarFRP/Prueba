# -*- coding: utf-8 -*-
from odoo import models, fields, Command, api, tools, _

class StockMove(models.Model):
    _inherit = 'stock.move'

    product_name = fields.Text(string='Descripción', compute='_compute_product_id_ventacero')

    @api.depends('product_id')
    def _compute_product_id_ventacero(self):
        for line in self:
            if not line.product_id:
                line.product_name = ''
            else:
                line.product_name = line.product_id.name
            