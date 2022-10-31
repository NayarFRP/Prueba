# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    quantity_uom_p = fields.Float(string="Cantidad a la mano", compute='_compute_fields_kg')
    available_quantity_uom_p = fields.Float(string="Cantidad disponible", compute='_compute_fields_kg')
    product_uom_uom_p = fields.Many2one('uom.uom', string="UdM Compra", compute='_compute_fields_kg')
    uom_category_id = fields.Many2one(related='product_uom_id.category_id')

    inventory_quantity_uom_p = fields.Float(string="Cantidades contadas")
    inventory_uom_id = fields.Many2one('uom.uom', string="UdM")
    inventory_diff_quantity_uom_p = fields.Float(string="Diferencia", compute='_compute_inventory_diff_quantity_uom_p', store=True,)

    note = fields.Char(string="Notas")

    @api.model
    def _get_inventory_fields_write(self):
        """ Returns a list of fields user can edit when editing a quant in `inventory_mode`."""
        res = super()._get_inventory_fields_write()
        res += ['quantity_uom_p', 'product_uom_uom_p', 'uom_category_id', 'inventory_quantity_uom_p', 'inventory_uom_id', 'inventory_diff_quantity_uom_p', 'note']
        return res

    @api.depends('quantity')
    def _compute_fields_kg(self):
        for line in self:
            line.quantity_uom_p = line.quantity * line.product_id.uom_po_id.ratio
            line.available_quantity_uom_p = line.available_quantity * line.product_id.uom_po_id.ratio
            line.product_uom_uom_p = line.product_id.uom_po_id.id

    @api.depends('inventory_quantity_uom_p', 'inventory_uom_id')
    def _compute_inventory_diff_quantity_uom_p(self):
        for line in self:
            if line.inventory_uom_id.ratio:
                line.inventory_quantity = line.inventory_quantity_uom_p / line.inventory_uom_id.ratio

            if line.inventory_uom_id == line.product_uom_id:
                line.inventory_diff_quantity_uom_p = line.inventory_quantity_uom_p - line.quantity
            else:
                line.inventory_diff_quantity_uom_p = line.inventory_quantity_uom_p - line.quantity_uom_p

    def action_set_inventory_quantity_to_zero(self):
        res = super().action_set_inventory_quantity_to_zero()

        self.inventory_quantity_uom_p = 0
        self.inventory_uom_id = False
        self.inventory_diff_quantity_uom_p = 0
        self.user_id = False
        self.note = False

        return res

    def action_apply_inventory(self):
        res = super().action_apply_inventory()
        self.action_set_inventory_quantity_to_zero()
        return res


    def _get_inventory_move_values(self, qty, location_id, location_dest_id, out=False):
        result = super(StockQuant, self)._get_inventory_move_values(qty, location_id, location_dest_id, out)

        if self.note and self.user_id:
            result['origin'] = self.note + " - " + self.user_id.name

        return result

