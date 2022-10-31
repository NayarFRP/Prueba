# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class AccountCashControlBalance(models.Model):
    _name = 'account.cash.control.balance'
    _description = 'Balance de control de caja'

    cash_control_id = fields.Many2one('account.cash.control', string='Control de caja')
    journal_id = fields.Many2one('account.journal', string='Diario')
    initial_balance = fields.Float(string="Saldo inicial")
    sale_balance = fields.Float(string="Ventas")
    in_balance = fields.Float(string="Ingresos")
    out_balance = fields.Float(string="Retiros")
    ending_balance = fields.Float(string="Saldo final", store=True, compute='_compute_ending_balance')

    @api.depends('initial_balance', 'sale_balance', 'in_balance', 'out_balance')
    def _compute_ending_balance(self):
        for line in self:
            line.ending_balance = line.initial_balance + line.sale_balance + line.in_balance - line.out_balance
            