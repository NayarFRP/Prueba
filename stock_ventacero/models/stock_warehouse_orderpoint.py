# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockWarehouseOrderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    onHandKg = fields.Float(string="A la mano (Kg)", compute='_compute_fields_kg')
    forcast_kg = fields.Float(string="Pronóstico (Kg)", compute='_compute_fields_kg')
    product_min_kg = fields.Float(string="Cantidad mínima (Kg)")
    product_max_kg = fields.Float(string="Cantidad máxima (Kg)")
    qty_multiple_kg = fields.Float(string="Cantidad múltiple (Kg)")
    qty_to_order_kg = fields.Float(string="Por ordenar (Kg)")


    @api.depends('qty_on_hand')
    def _compute_fields_kg(self):
        for line in self:
            line.onHandKg = line.qty_on_hand * line.product_id.weight
            line.forcast_kg = line.qty_forecast * line.product_id.weight

    @api.onchange('product_min_kg')
    def _onchange_product_min_kg(self):
        if self.product_id.weight > 0:
            self.product_min_qty = self.product_min_kg / self.product_id.weight


    @api.onchange('product_max_kg')
    def _onchange_product_max_kg(self):
        if self.product_id.weight > 0:
            self.product_max_qty = self.product_max_kg / self.product_id.weight

    @api.onchange('qty_multiple_kg')
    def _onchange_qty_multiple_kg(self):
        if self.product_id.weight > 0:
            self.qty_multiple = self.qty_multiple_kg / self.product_id.weight

    @api.onchange('qty_to_order')
    def _onchange_qty_to_order(self):
        self.qty_to_order_kg = self.qty_to_order * self.product_id.weight

