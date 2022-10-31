# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'


    @api.depends('product_id', 'order_id.date_order', 'order_id.partner_id')
    def _compute_analytic_tag_ids(self):
        for line in self:
            if not line.display_type and line.state == 'draft':
                default_analytic_account = line.env['account.analytic.default'].sudo().account_get(
                    product_id=line.product_id.id,
                    partner_id=line.order_id.partner_id.id,
                    date=line.order_id.date_order,
                    company_id=line.company_id.id,
                    warehouse_id=line.order_id.warehouse_id.id,
                )
                line.analytic_tag_ids = default_analytic_account.analytic_tag_ids

