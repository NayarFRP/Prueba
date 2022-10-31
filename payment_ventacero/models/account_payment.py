# -*- coding: utf-8 -*-
from odoo import models, api, fields
import logging

_logger = logging.getLogger(__name__)

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    payment_batch_id = fields.Many2one('account.payment.batch', string="Lote de pago", compute='_compute_get_payment_batch')
    id_payment_batch = fields.Char('id de pago por lote')


    @api.depends('reconciled_bill_ids', 'ref')
    def _compute_get_payment_batch(self):
        for payment in self:
            if not payment.payment_batch_id:
                if payment.state == 'posted':
                    if payment.reconciled_bill_ids:
                        for line in payment.reconciled_bill_ids:
                            if line.payment_batch_id:
                                payment.update({
                                    'payment_batch_id': line.payment_batch_id,
                                })
                                break
                    elif payment.id_payment_batch:
                        payment_batch = self.env['account.payment.batch'].search([('id', '=', payment.id_payment_batch)])
                        if payment_batch:
                            payment.update({
                                'payment_batch_id': payment_batch.id,
                            })
