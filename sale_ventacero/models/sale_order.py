# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from datetime import timedelta

import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    #Reporte "Presupuestos"
    equivalent_weight = fields.Float(string="Peso equivalente", compute='_equivalent_weight', store=True)
    total_discount = fields.Float(string="Descuento total", compute='_compute_total_discount', store=True)
    
    #Reporte "Pedidos"
    equivalent_weight_to_deliver = fields.Float(string="Peso equivalente por entregar", compute='_equivalent_weight', store=True)
    amount_pending_delivery = fields.Float(string="Importe del pendiente por entregar", compute='_equivalent_weight', store=True)


    home_delivery = fields.Boolean("Entrega a domicilio")


    @api.depends('order_line.product_id', 'order_line.qty_delivered')
    def _equivalent_weight(self):
        for order in self:
            equivalent_weight =  0.0
            equivalent_weight_delivered =  0.0
            amount_pending_delivery = 0.0
            for line in order.order_line:
                _logger.info('ENTRO A LINEA PARA CALCULO DE PESO')
                discount = 0.0
                if line.discount:
                    discount = (100 - line.discount) / 100
                equivalent_weight += (line.product_uom_qty / line.product_uom.ratio)*line.product_id.equivalent_weight
                equivalent_weight_delivered += (line.qty_delivered / line.product_uom.ratio)*line.product_id.equivalent_weight
                amount_pending_delivery += ((line.product_uom_qty - line.qty_delivered)*line.price_unit) * discount
            _logger.info('ESTO SUMO' + str(equivalent_weight))
            order.update({
                'equivalent_weight': equivalent_weight/1000,
                'equivalent_weight_to_deliver': (equivalent_weight - equivalent_weight_delivered)/1000,
                'amount_pending_delivery': amount_pending_delivery
            })

    @api.depends('amount_total')
    def _compute_total_discount(self):
        for order in self:
            _logger.info('ENTRO A ORDEN PARA CALCULO DE DESCUENTO')
            order.update({
                'total_discount': order.amount_undiscounted - order.amount_untaxed,
            })

    def action_confirm(self):
        result = super(SaleOrder, self).action_confirm()
        for so in self:
            if so.home_delivery:
                if so.warehouse_id.entrega_turnos:
                    if not so.commitment_date:
                        fecha = datetime.now(tz=None)
                        while True:
                            _logger.info('### FECHA: ' + str(fecha))
                            while True:
                                if fecha.weekday() == 5:
                                    fecha += timedelta(days=1)
                                    fecha = fecha.replace(hour=18, minute=0, second=0, microsecond=0)
                                    _logger.info('### ES SABADO SE AUMENTA UN DIA Y HORA A LAS 8')
                                elif fecha.weekday() == 6:
                                    fecha += timedelta(days=1)
                                    fecha = fecha.replace(hour=18, minute=0, second=0, microsecond=0)
                                    _logger.info('### ES DOMINGO SE AUMENTA UN DIA Y HORA A LAS 8')
                                    break
                                elif fecha.hour >= 13 and fecha.hour < 18:
                                    fecha = fecha.replace(hour=23, minute=0, second=0, microsecond=0)
                                    _logger.info('### ASIGNACION A TARDE')
                                    break
                                elif fecha.hour >= 18 and fecha.hour < 23:
                                    fecha += timedelta(days=1)
                                    fecha = fecha.replace(hour=18, minute=0, second=0, microsecond=0)
                                    _logger.info('### ASIGNACION AL SIGUIENTE DIA EN LA MAÑANA')
                                    break
                                else:
                                    fecha -= timedelta(hours=1)

                            cerrado = self.sudo().env['delivery.shift'].search_count([('date_start', '<=', fecha), ('date_stop', '>', fecha)])
                            _logger.info('### CERRADO: ' + str(cerrado))

                            if cerrado == 0:
                                so.commitment_date = fecha
                                break
                    else:
                        fecha = so.commitment_date

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
                            so.commitment_date = fecha
                        else:
                            raise ValidationError(_("Turno cerrado"))
                else:
                    raise ValidationError(_("El almacen " + so.warehouse_id.name + " no acepta ordenes con entrega a domicilio"))


        return result


    @api.onchange('team_id')
    def _on_change_team_id(self):
        for order in self:
            if not order.partner_id:
                order.warehouse_id = order.team_id.warehouse_id.id
                order.partner_id = order.team_id.customer_id.id

    @api.onchange('home_delivery')
    def _on_change_home_delivery(self):
        for order in self:
            if order.home_delivery:
                return {
                    'warning': {
                        'title': 'Entrega a domicilio',
                        'message': 'No olvides capturar correctamente el campo "Dirección de entrega"'
                    }
                }


    def change_delivery_date(self):
        return {
            'res_model': 'wizard.change.date',
            'view_mode': 'form',
            'context': {
                'active_model': 'sale.order',
                'active_id': self.id,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
            }
