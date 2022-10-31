# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    pricelist_id = fields.Many2one(string="Lista de precios", related="order_partner_id.property_product_pricelist")
    partner_category_id = fields.Many2many(string="Categorias", related="order_partner_id.category_id")
    team_id = fields.Many2one(string="Categorias", related="order_id.team_id")
    product_category_id = fields.Many2one(string="Categoria de producto", related="product_id.categ_id")
    equivalent_weight = fields.Float(string="Peso equivalente", compute='_equivalent_weight', store=True)
    amount_discount = fields.Float(string="Monto de descuento", compute='_equivalent_weight', store=True)
    product_cost = fields.Float(string="Costo", compute='_equivalent_weight', store=True)
    contribucion = fields.Float(string="Contribucion", compute='_equivalent_weight', store=True)
    margen = fields.Float(string="Margen", compute='_equivalent_weight', store=True)

    @api.depends('product_id', 'product_uom_qty', 'discount', 'price_unit', 'state')
    def _equivalent_weight(self):
        for line in self:
            equivalent_weight = (line.product_uom_qty / line.product_uom.ratio)*line.product_id.equivalent_weight
            amount_discount = (line.product_uom_qty * line.price_unit) * (line.discount / 100)
            costo = (line.product_uom_qty / line.product_uom.ratio) * line.product_id.standard_price
            contribucion = line.price_subtotal - costo
            margen = (contribucion * 100) / costo if costo > 0 else 0
            line.update({
                'equivalent_weight': equivalent_weight,
                'amount_discount': amount_discount,
                'product_cost': costo,
                'contribucion': contribucion,
                'margen': margen,
            })



