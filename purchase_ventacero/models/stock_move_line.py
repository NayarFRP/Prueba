# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    demand_qty = fields.Float(string="Demanda", compute='_compute_demand_qty')

    @api.onchange('product_id', 'product_uom_id')
    def _onchange_product_id(self):
        """Se sobreescribe funcion para tomar la unidad de medida de compra en la ventana de recepcion cuando
        no tienes operaciones detalladas"""
        if self.product_id:
            if self.picking_id:
                product = self.product_id.with_context(lang=self.picking_id.partner_id.lang or self.env.user.lang)
                self.description_picking = product._get_description(self.picking_id.picking_type_id)
            self.lots_visible = self.product_id.tracking != 'none'
            if not self.product_uom_id or self.product_uom_id.category_id != self.product_id.uom_id.category_id:
                if self.move_id.product_uom:
                    if self.move_id.purchase_line_id:
                        self.product_uom_id = self.move_id.purchase_line_id.product_uom.id
                    else:
                        self.product_uom_id = self.move_id.product_uom.id
                else:
                    self.product_uom_id = self.product_id.uom_id.id


    @api.depends('move_id.product_uom_qty')
    def _compute_demand_qty(self):
        for line in self:
            demand = line.move_id.product_uom_qty * line.product_uom_id.ratio

            line.update({
                'demand_qty': demand,
            })
