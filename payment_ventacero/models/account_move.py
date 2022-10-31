# -*- coding: utf-8 -*-
from odoo import models, api, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    payment_batch_id = fields.Many2one('account.payment.batch', string="Lote de pago")
    