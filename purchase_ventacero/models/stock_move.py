# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockMove(models.Model):
    _inherit = 'stock.move'

    demand_uom_p = fields.Float(string="Demanda", compute='_compute_purchase_fields', store=True, compute_sudo=True)
    done_uom_p = fields.Float(string="Hecho", compute='_compute_purchase_fields', store=True, compute_sudo=True)
    product_uom_p = fields.Many2one('uom.uom', string="UdM Compra", compute='_compute_purchase_fields')

    @api.depends('product_uom_qty', 'product_uom', 'quantity_done')
    def _compute_purchase_fields(self):
        for line in self:
            if line.product_uom == line.product_id.uom_id:
                line.demand_uom_p = (line.product_uom_qty * line.product_id.uom_po_id.ratio)
                line.done_uom_p = (line.quantity_done * line.product_id.uom_po_id.ratio)
                line.product_uom_p = line.product_id.uom_po_id.id
            else:
                line.demand_uom_p = line.product_uom_qty
                line.done_uom_p = line.quantity_done
                line.product_uom_p = line.product_id.uom_po_id.id
                