# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class AccountCashControlTransfers(models.Model):
    _name = 'account.cash.control.transfers'
    _description = 'Tranferencias en control de caja'

    cash_control_id = fields.Many2one('account.cash.control', string='Control de caja')
    name = fields.Char("Descripción")
    journal_orig_id = fields.Many2one('account.journal', string='Origen')
    journal_dest_id = fields.Many2one('account.journal', string='Destino')
    amount = fields.Float(string="Importe")
  