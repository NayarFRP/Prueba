# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class StockMove(models.Model):
    _inherit = 'stock.move'

    purchase_id = fields.Many2one(string="Pedido de compra", related="purchase_line_id.order_id")
    supplier_id = fields.Many2one(string="Proveedor", related="purchase_line_id.partner_id")
    product_category_id = fields.Many2one(string="Categoría de producto", related="product_id.categ_id")
    price_unit_uom_p = fields.Float(string="Precio unitario", related="purchase_line_id.price_unit")


    def action_view_picking_id(self):
        for line in self:
            if line.picking_id:
                return {
                    "type":"ir.actions.act_window",
                    "res_model": "stock.picking",
                    "views": [[False, "form"]],
                    "res_id": line.picking_id.id,
                    "target": "current",
                }

    def action_view_purchase_id(self):
        for line in self:
            if line.purchase_id:
                return {
                    "type":"ir.actions.act_window",
                    "res_model": "purchase.order",
                    "views": [[False, "form"]],
                    "res_id": line.purchase_id.id,
                    "target": "current",
                }

    def action_cancel_move(self):
        for line in self:
            if line.state not in ['done', 'cancel']:
                line.update({
                    'state': 'cancel'
                })