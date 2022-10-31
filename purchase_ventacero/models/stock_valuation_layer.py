# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockValuationLayer(models.Model):
    _inherit = 'stock.valuation.layer'

    quantity_uom_p = fields.Float(string="Cantidad", compute='_compute_purchase_fields', store=True, compute_sudo=True)
    product_uom_p = fields.Many2one('uom.uom', string="UdM Compra", compute='_compute_purchase_fields')
    unit_cost_uom_p = fields.Monetary(string="Valor unitario UdM Compra", compute='_compute_unit_cost_uom_p', store=True, compute_sudo=True)


    @api.depends('quantity')
    def _compute_purchase_fields(self):
        for line in self:
            line.quantity_uom_p = (line.quantity * line.product_id.uom_po_id.ratio)
            line.product_uom_p = line.product_id.uom_po_id.id

    @api.depends('unit_cost')
    def _compute_unit_cost_uom_p(self):
        for line in self:
            line.unit_cost_uom_p = line.unit_cost / line.product_uom_p.ratio
