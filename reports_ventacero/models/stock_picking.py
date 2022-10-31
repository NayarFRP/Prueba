# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    warehouse_origin = fields.Many2one(string="Almacén origen", related="location_id.warehouse_id")
    warehouse_dest = fields.Many2one(string="Almacén destino", related="location_dest_id.warehouse_id")
    internal_transfer = fields.Boolean(string="Transferencia entre sucursales", related="picking_type_id.internal_transfer")
    equivalent_weight = fields.Float(string="Peso equivalente", compute='_equivalent_weight_picking', store=True)
    amount_products = fields.Float(string="Importe", compute='_equivalent_weight_picking', store=True)
    nivel_de_servicio = fields.Selection([
        ('en_tiempo', 'En tiempo'),
        ('fuera_de_tiempo', 'Fuera de tiempo'),
    ], string='Nivel de servicio', compute="_compute_nivel_servicio")
    account_move_ids = fields.Many2many('account.move', string="Facturas")


    @api.depends('move_ids_without_package.product_id', 'move_ids_without_package.product_uom_qty')
    def _equivalent_weight_picking(self):
        for order in self:
            equivalent_weight =  0.0
            importe = 0.0
            for line in order.move_ids_without_package:
                equivalent_weight += (line.product_uom_qty / line.product_uom.ratio)*line.product_id.equivalent_weight
                importe += (line.product_uom_qty / line.product_uom.ratio) * line.product_id.standard_price

            order.update({
                'equivalent_weight': equivalent_weight/1000,
                'amount_products': importe
            })


    def action_view_picking_id(self):
        for line in self:
            return {
                "type":"ir.actions.act_window",
                "res_model": "stock.picking",
                "views": [[False, "form"]],
                "res_id": line.id,
                "target": "current",
            }


    @api.depends('scheduled_date')
    def _compute_nivel_servicio(self):
        for reg in self:
            status = ''

            for registro in reg.account_move_ids:
                reg.write({'account_move_ids': [(3, registro.id)]})

            invoice_list = self.sudo().env['account.move'].search([('invoice_origin', '=', reg.origin), ('state', '=', 'posted')])
            if invoice_list:
                for invoice in invoice_list:
                    reg.write({'account_move_ids': [(4, invoice.id)]})

            if reg.scheduled_date < datetime.now(tz=None):
                status = 'en_tiempo'
            if reg.scheduled_date >= datetime.now(tz=None):
                status = 'fuera_de_tiempo'

            reg.update({
                'nivel_de_servicio': status
            })
    