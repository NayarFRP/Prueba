# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime

import logging

_logger = logging.getLogger(__name__)

class DeliveryShift(models.Model):
    _name = 'delivery.shift'

    name = fields.Char(string="Nombre", compute="_compute_dates")
    date = fields.Datetime(string="Fecha")
    date_start = fields.Datetime(string="Inicio", compute="_compute_dates", store=True)
    date_stop = fields.Datetime(string="Fin", compute="_compute_dates", store=True)
    turno = fields.Selection([
        ('1', "Mañana"),
        ('2', "Tarde"),
    ], default='1')
    sucursal = fields.Many2one('res.partner', string="Sucursal")


    @api.model
    def create(self, vals):
        result = super(DeliveryShift, self).create(vals)

        turnos = self.sudo().env['delivery.shift'].search_count([('date_start', '=', result.date_start), ('date_stop', '=', result.date_stop)])

        _logger.info('### CUANTOOOOOS: ' + str(turnos))
        if turnos > 1:
            raise ValidationError(_("Turno cerrado anteriormente"))

        return result

    @api.depends('date', 'turno')
    def _compute_dates(self):
        for event in self:
            if event.date and event.turno:
                if event.turno == '1':
                    event.name = 'Mañana'
                    event.date_start = event.date.replace(hour=13, minute=0, second=0, microsecond=0)
                    event.date_stop = event.date.replace(hour=18, minute=0, second=0, microsecond=0)
                elif event.turno == '2':
                    event.name = 'Tarde'
                    event.date_start = event.date.replace(hour=18, minute=0, second=0, microsecond=0)
                    event.date_stop = event.date.replace(hour=23, minute=0, second=0, microsecond=0)
            else:
                event.name = 'New'
                event.date_start = False
                event.date_stop = False

