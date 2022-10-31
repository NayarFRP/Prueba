# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class StockValuationLayer(models.Model):
    _inherit = 'stock.valuation.layer'

    kardex_description = fields.Char(string='Descripción', compute='_compute_cantidades', store=True)
    entrada_c = fields.Float(string='Entrada', compute='_compute_cantidades', store=True)
    salida_c = fields.Float(string='Salida', compute='_compute_cantidades', store=True)
    saldo_c = fields.Float(string='Saldo', compute='_compute_cantidades', store=True)
    entrada_s = fields.Float(string='Entrada', compute='_compute_cantidades', store=True)
    salida_s = fields.Float(string='Salida', compute='_compute_cantidades', store=True)
    saldo_s = fields.Float(string='Saldo', compute='_compute_cantidades', store=True)
    costo_promedio = fields.Float(string='Costo promedio', compute='_compute_costo_promedio', store=True)


    @api.depends('quantity', 'entrada_c', 'salida_c', 'entrada_s', 'salida_s')
    def _compute_cantidades(self):
        for reg in self:
            # kardex_description
            reg.kardex_description = reg.stock_move_id.reference
            # entrada_c, salida_c
            if reg.quantity_uom_p >= 0:
                reg.entrada_c = reg.quantity_uom_p
                reg.salida_c = 0
            else:
                reg.entrada_c = 0
                reg.salida_c = reg.quantity_uom_p * -1
            
            # saldo_c
            saldo = self.sudo().env['product.product'].search([('id', '=', reg.product_id.id)])
            reg.saldo_c = saldo[0].qty_available * reg.product_uom_p.ratio if saldo else 0

            # entrada_s, salida_s
            if reg.value >= 0:
                reg.entrada_s = reg.value
                reg.salida_s = 0
            else:
                reg.entrada_s = 0
                reg.salida_s = reg.value * -1

            # saldo_s
            ultimo_saldo = self.sudo().env['stock.valuation.layer'].search([('id', '!=', reg.id),('product_id', '=', reg.product_id.id)])
            _logger.info('###### ULTIMO: ' + str(ultimo_saldo))
            if ultimo_saldo:
                reg.saldo_s = ultimo_saldo[-1].saldo_s + reg.entrada_s - reg.salida_s
            else:
                reg.saldo_s = 0 + reg.entrada_s - reg.salida_s

    @api.depends('account_move_id', 'value')
    def _compute_costo_promedio(self):
        for reg in self:
            # costo_promedio
            reg.costo_promedio = reg.product_id.standard_price / reg.product_id.uom_po_id.ratio
            _logger.info('###### PROMEDIO: ' + str(reg.costo_promedio))


