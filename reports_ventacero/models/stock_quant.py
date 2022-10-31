# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    product_name = fields.Char(string="Nombre", related="product_id.name")
    weight = fields.Float(string="Peso", related="product_id.weight")
    warehouse_incoming = fields.Float(string="Entradas", compute='_compute_in_and_out_qtys')
    warehouse_outgoing = fields.Float(string="Comprometido", compute='_compute_in_and_out_qtys')
    mrp_available_quantity = fields.Float(string="Disponible", compute='_compute_mrp_available_quantity')
    unit_cost = fields.Float(string="Costo promedio", compute='_compute_unit_cost')


    @api.depends('product_id.virtual_available')
    def _compute_in_and_out_qtys(self):
        for reg in self:
            outgoing = 0
            incoming = 0

            moves_out = reg.sudo().env['stock.move'].search([('state', 'in', ('waiting', 'confirmed', 'assigned', 'partially_available')), ('product_id', '=', reg.product_id.id), ('picking_code', '=', 'outgoing'), ('location_id', '=', reg.location_id.id)])
            moves_in = reg.sudo().env['stock.move'].search([('state', 'in', ('waiting', 'confirmed', 'assigned', 'partially_available')), ('product_id', '=', reg.product_id.id), ('picking_code', '=', 'incoming'), ('location_dest_id', '=', reg.location_id.id)])

            if moves_out:
                for line in moves_out:
                    outgoing += line.demand_uom_p

            if moves_in:
                for line in moves_in:
                    incoming += line.demand_uom_p

            reg.update({
                'warehouse_incoming': incoming,
                'warehouse_outgoing': outgoing,
            })

    @api.depends('quantity_uom_p', 'warehouse_incoming', 'warehouse_outgoing')
    def _compute_mrp_available_quantity(self):
        for reg in self:
            reg.update({
                'mrp_available_quantity': reg.quantity_uom_p + reg.warehouse_incoming - reg.warehouse_outgoing,
            })

    @api.depends('product_id.standard_price')
    def _compute_unit_cost(self):
        for reg in self:
            reg.unit_cost = reg.product_id.standard_price / reg.product_id.uom_po_id.ratio