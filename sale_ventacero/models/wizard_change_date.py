# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from datetime import date

import logging

_logger = logging.getLogger(__name__)

class WizardChangeDate(models.TransientModel):
    _name = 'wizard.change.date'
    _description = 'Boton cambiar fecha de entrega'

    date = fields.Datetime(string="Fecha", default=datetime.today())


    def b_aceptar(self):
        orden = self.sudo().env['sale.order'].browse(self._context.get('active_id', []))

        for line in orden.picking_ids:
            if line.state not in ['done', 'cancel']:
                fecha = self.date

                if fecha < datetime.now(tz=None):
                    raise ValidationError(_("Turno cerrado"))

                _logger.info('### FECHA: ' + str(fecha))

                cerrado = self.sudo().env['delivery.shift'].search_count([('date_start', '<=', fecha), ('date_stop', '>', fecha)])
                _logger.info('### CERRADO: ' + str(cerrado))

                if cerrado == 0:
                    if fecha.hour >= 13 and fecha.hour < 18:
                        fecha = fecha.replace(hour=18, minute=0, second=0, microsecond=0)
                    elif fecha.hour >= 18 and fecha.hour < 23:
                        fecha = fecha.replace(hour=23, minute=0, second=0, microsecond=0)
                    else:
                        fecha = fecha.replace(hour=23, minute=0, second=0, microsecond=0)
                    line.date_deadline = fecha
                else:
                    raise ValidationError(_("Turno cerrado"))
