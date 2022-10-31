# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class AccountCashControlClose(models.Model):
    _name = 'account.cash.control.close'
    _description = 'lineas de cierre en control de caja'

    cash_control_id = fields.Many2one('account.cash.control', string='Control de caja')
    journal_id = fields.Many2one('account.journal', string='Diario')
    expected_amount = fields.Float(string="Monto esperado")
    counted_amount = fields.Float(string="Monto contado")
    diference = fields.Float(string="Diferencia", compute='_compute_diference')


    @api.depends('counted_amount')
    def _compute_diference(self):
        total = 0
        for reg in self:
            diference = reg.counted_amount - reg.expected_amount

            reg.update({
                'diference': diference,
            })
  