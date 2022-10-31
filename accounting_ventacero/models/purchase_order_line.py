# -*- coding: utf-8 -*-
from odoo import models, api, fields

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    account_analytic_account_ids = fields.Many2many(related='order_id.user_id.account_analytic_account_ids')
    account_analytic_tag_ids = fields.Many2many(related='order_id.user_id.account_analytic_tag_ids')
    