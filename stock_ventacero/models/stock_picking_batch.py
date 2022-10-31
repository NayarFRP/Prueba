# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockPickingBatch(models.Model):
    _inherit = 'stock.picking.batch'

    entradaCamion = fields.Datetime(string="Entrada de camión")
    salidaCamion = fields.Datetime(string="Salida de camión")
    referenciaEntrada = fields.Char(string="Referencia de entrada")
    ticketBascula = fields.Char(string="Ticket de bascula")
    pesoTicket = fields.Float(string="Peso en ticket")
    transportista_id = fields.Many2one('res.partner', string="Transportista")
    montacarguista_id = fields.Many2one('res.partner', string="Montacarguista")
    jefeAlmacen_id = fields.Many2one('res.partner', string="Jefe de almacén")
    note = fields.Html('Notes')
    