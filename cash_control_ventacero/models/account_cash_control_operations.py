# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class AccountCashControlOperations(models.Model):
    _name = 'account.cash.control.operations'
    _description = 'Operaciones en control de caja'

    cash_control_id = fields.Many2one('account.cash.control', string='Control de caja')
    payment_id = fields.Many2one('account.payment', string='Pago')
    name = fields.Char(string='Descripción')
    journal_id = fields.Many2one('account.journal', string='Diario')
    partner_id = fields.Many2one('res.partner', string='Cliente')
    l10n_mx_edi_payment_method_id = fields.Many2one('l10n_mx_edi.payment.method', string='Forma de pago')
    amount = fields.Float(string="Importe")
    #account_move_ids = fields.Many2many('account.move', string="Facturas")
    state = fields.Selection(string="Estado de pago", related="payment_id.state")
  