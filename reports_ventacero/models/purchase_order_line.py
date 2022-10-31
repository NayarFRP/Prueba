# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    warehouse_id = fields.Many2one(string="Almacén", related="order_id.picking_type_id.warehouse_id")
    location_id = fields.Many2one(string="Ubicación", related="order_id.picking_type_id.default_location_dest_id")
    product_category_id = fields.Many2one(string="Categoría de producto", related="product_id.categ_id")

