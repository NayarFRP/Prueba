# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'


    @api.depends('partner_id', 'date_order', 'warehouse_id')
    def _compute_analytic_account_id(self):
        for order in self:
            default_analytic_account = order.env['account.analytic.default'].sudo().account_get(
                partner_id=order.partner_id.id,
                date=order.date_order,
                company_id=order.company_id.id,
                warehouse_id=order.warehouse_id.id,
            )
            order.analytic_account_id = default_analytic_account.analytic_id




