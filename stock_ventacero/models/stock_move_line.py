# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'


    @api.model
    def create(self, vals):
        res = super(StockMoveLine, self).create(vals)

        if res.move_id.purchase_line_id:
            res.product_uom_id = res.move_id.purchase_line_id.product_uom.id
            
        return res