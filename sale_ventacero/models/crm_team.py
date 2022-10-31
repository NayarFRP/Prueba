# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class CrmTeam(models.Model):
    _inherit = 'crm.team'

    partner_id = fields.Many2one('res.partner', string="Dirección de sucursal")
    warehouse_id = fields.Many2one('stock.warehouse', string='Almacén')
    customer_id = fields.Many2one('res.partner', string='Cliente por defecto')
    show_discount = fields.Boolean(string="Mostrar descuento")
    ticket_message = fields.Text(string='Frase de agradecimiento en ticket')

    