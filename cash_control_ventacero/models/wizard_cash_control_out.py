# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from datetime import date

class WizardCashControlOut(models.TransientModel):
    _name = 'wizard.cash.control.out'
    _description = 'Boton retiro de efectivo'

    name = fields.Char("Descripción", default="Retiro parcial a caja de retiro")
    amount = fields.Float(string="Importe")


    def b_aceptar(self):
        caja_id = self.sudo().env['account.cash.control'].browse(self._context.get('active_id', []))
        balance_origen = self.sudo().env['account.cash.control.balance'].search([('cash_control_id', '=', caja_id.id), ('journal_id.type', '=', 'cash'), ('journal_id.caja_retiro', '=', False)])
        balance_destino = self.sudo().env['account.cash.control.balance'].search([('cash_control_id', '=', caja_id.id), ('journal_id.type', '=', 'cash'), ('journal_id.caja_retiro', '=', True)])

        if balance_origen.ending_balance < self.amount:
            raise ValidationError(_("No hay suficiente efectivo"))

        #SE ACTUALIZAN LINEAS DE BALANCE
        balance_origen.write({
            'out_balance': balance_origen.out_balance + self.amount,
        })
        balance_destino.write({
            'in_balance': balance_destino.in_balance + self.amount,
        })

        #SE CREA LINEA EN TRANSFERENCIAS
        values = {
            'cash_control_id': caja_id.id,
            'name': self.name,
            'journal_orig_id': balance_origen.journal_id.id,
            'journal_dest_id': balance_destino.journal_id.id,
            'amount': 0 + self.amount,
        }
        transfers_line = self.sudo().env['account.cash.control.transfers'].create(values)
