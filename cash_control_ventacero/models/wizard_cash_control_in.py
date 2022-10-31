# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from datetime import date

class WizardCashControlIn(models.TransientModel):
    _name = 'wizard.cash.control.in'
    _description = 'Boton ingreso de efectivo'

    name = fields.Char("Descripción", default="Ingreso de efectivo de caja de retiro")
    amount = fields.Float(string="Importe")


    def b_aceptar(self):
        caja = self.sudo().env['account.cash.control'].browse(self._context.get('active_id', []))
        balance_inicial = self.sudo().env['account.cash.control.balance'].search([('cash_control_id', '=', caja.id), ('journal_id.type', '=', 'cash'), ('journal_id.caja_retiro', '=', True)])
        balance_destino = self.sudo().env['account.cash.control.balance'].search([('cash_control_id', '=', caja.id), ('journal_id.type', '=', 'cash'), ('journal_id.caja_retiro', '=', False)])

        if balance_inicial.ending_balance < self.amount:
            raise ValidationError(_("No hay suficiente efectivo en caja de retiro"))

        #SE ACTUALIZAN LINEAS DE BALANCE
        balance_inicial.write({
            'out_balance': balance_inicial.out_balance + self.amount,
        })
        balance_destino.write({
            'in_balance': balance_destino.in_balance + self.amount,
        })

        #SE CREA LINEA EN TRANSFERENCIAS
        values = {
            'cash_control_id': caja.id,
            'name': self.name,
            'journal_orig_id': balance_inicial.journal_id.id,
            'journal_dest_id': balance_destino.journal_id.id,
            'amount': 0 + self.amount,
        }
        transfers_line = self.sudo().env['account.cash.control.transfers'].create(values)

     