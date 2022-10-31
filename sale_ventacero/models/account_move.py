# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        res = super(AccountMove, self).action_post()

        sale_order = self.env['sale.order'].search([('name', '=', self.invoice_origin)])
        _logger.info('######'+ str(sale_order))

        if sale_order:
            if not sale_order.home_delivery:
                if sale_order.team_id.warehouse_id.id == sale_order.warehouse_id.id:
                    entregas = self.env['stock.picking'].search([('origin', '=', self.invoice_origin), ('state', '=', 'waiting')])
                    if entregas:
                        raise ValidationError(_("No hay existencia en almacén"))
                    else:
                        entregas = self.env['stock.picking'].search([('origin', '=', self.invoice_origin), ('state', '=', 'assigned')])

                        for entrega in entregas:
                            entrega.action_set_quantities_to_reservation()

                            for line in entrega.move_ids_without_package:
                                if line.quantity_done < line.product_uom_qty:
                                    raise ValidationError(_("No hay existencia en almacén, revise la orden de entrega"))

                            entrega.button_validate()

        return res


    def action_print_ticket(self):
        return self.env.ref('sale_ventacero.report_invoice_ticket').report_action(self)
        