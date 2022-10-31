# -*- coding: utf-8 -*-
from odoo import models, api, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    l10n_mx_edi_payment_method_id = fields.Many2one(related='partner_id.l10n_mx_edi_payment_method_id')
    l10n_mx_edi_usage = fields.Selection(related='partner_id.l10n_mx_edi_usage')
    