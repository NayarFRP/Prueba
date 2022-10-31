# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    weight = fields.Float(string="Peso", compute='_compute_line_weight')

    @api.depends('product_uom_qty', 'product_uom')
    def _compute_line_weight(self):
        for line in self:
            if line.product_id.uom_id.id == line.product_uom.id:
                line.weight = line.product_id.uom_po_id.ratio * line.product_uom_qty
            else:
                line.weight = line.product_uom_qty
