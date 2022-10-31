# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountPaymentBatchLine(models.Model):
    _name = 'account.payment.batch.line'
    _description = 'Linea de lote de pago'

    payment_batch_id = fields.Many2one('account.payment.batch', string="Lote de pago")
    partner_id = fields.Many2one('res.partner', string="Empresa")
    ref = fields.Char('Referencia')
    bank_account_id = fields.Many2one('res.partner.bank', string="Cuenta bancaria")
    account_move_ids = fields.Many2many('account.move')
    date = fields.Date('Fecha')
    amount = fields.Float('Importe')
    currency_id = fields.Many2one('res.currency', string="Moneda")
    amount_tax = fields.Float('Importe de impuesto')
    state = fields.Selection(related="payment_batch_id.state", string='Estado')
    

    
    