# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class StockPickingBatch(models.Model):
    _inherit = 'stock.picking.batch'

    tipo_de_transporte = fields.Char(string="Tipo de transporte")
    unidad = fields.Char(string="Unidad")
    km_inicial = fields.Float(string="Km. inicial")

    destino = fields.Char(string="Destino")
    km_destino = fields.Float(string="Km")

    kilos = fields.Float(string="Kilos", compute="_compute_embarque_data")
    cantidad_facturas = fields.Float(string="Cantidad de facturas", compute="_compute_embarque_data")
    cantidad_lineas = fields.Float(string="Cantidad de lineas", compute="_compute_embarque_data")
    cantidad_lineas_entregadas = fields.Float(string="Cantidad de lineas entregadas", compute="_compute_embarque_data")
    
    nivel_de_servicio = fields.Selection([
        ('en_tiempo', 'En tiempo'),
        ('fuera_de_tiempo', 'Fuera de tiempo'),
    ], string='Nivel de servicio')

    estado_de_entrega = fields.Selection([
        ('cargado', 'Cargado'),
        ('en_ruta', 'En ruta'),
        ('entregado', 'Entregado'),
    ], string='Estado de entrega')


    @api.depends('picking_ids')
    def _compute_embarque_data(self):
        for reg in self:
            kilos = 0
            cantidad_facturas = 0
            cantidad_lineas = 0
            cantidad_lineas_entregadas = 0
            nivel_de_servicio = 'en_tiempo'

            for line in reg.picking_ids:
                kilos += line.weight

                invoice = self.sudo().env['account.move'].search_count([('invoice_origin', '=', line.origin), ('state', '=', 'posted')])
                if invoice:
                    cantidad_facturas = invoice

                for move in line.move_ids_without_package:
                    cantidad_lineas += 1
                    if move.quantity_done >= move.product_uom_qty:
                        cantidad_lineas_entregadas += 1

                if line.nivel_de_servicio == 'fuera_de_tiempo':
                    nivel_de_servicio = 'fuera_de_tiempo'

            reg.update({
                'kilos': kilos,
                'cantidad_facturas': cantidad_facturas,
                'cantidad_lineas': cantidad_lineas,
                'cantidad_lineas_entregadas': cantidad_lineas_entregadas,
                'nivel_de_servicio': nivel_de_servicio
            })