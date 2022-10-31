# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockReturnPickingLine(models.TransientModel):
    _inherit = 'stock.return.picking.line'

    return_qty = fields.Float(string="Cantidad")
    return_uom_id = fields.Many2one('uom.uom', string="Unidad de medida")
    uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')


    @api.onchange('return_qty', 'return_uom_id')
    def _compute_return_qty(self):
        for line in self:
            if line.return_uom_id.ratio:
                line.quantity = line.return_qty / line.return_uom_id.ratio
                line.to_refund = False
