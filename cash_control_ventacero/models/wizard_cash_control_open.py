# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from datetime import date

class WizardCashControlOpen(models.TransientModel):
    _name = 'wizard.cash.control.open'
    _description = 'Boton abrir caja'

    name = fields.Char("Descripción", default="Efectivo inicial")
    amount = fields.Float(string="Importe")


    def abrir_caja(self):
        caja = self.sudo().env['account.cash.control'].browse(self._context.get('active_id', []))
        linea = self.sudo().env['account.cash.control.balance'].search([('cash_control_id', '=', caja.id), ('journal_id.type', '=', 'cash'), ('journal_id.caja_retiro', '=', False)])

        current_date = date.today()
        caja_abierta = self.sudo().env['account.cash.control'].search([('team_id', '=', caja.team_id.id), ('date', '=', current_date)])

        if caja_abierta:
            raise ValidationError(_("Ya existe una caja abierta para esta sucursal"))

        linea.write({
            'initial_balance': self.amount,
        })

        caja.update({
            'date_begin': datetime.today(),
            'date': date.today(),
            'state': 'open',
        })

        values = {
            'cash_control_id': caja.id,
            'name': self.name,
            'journal_id': linea.journal_id.id,
            'l10n_mx_edi_payment_method_id': linea.journal_id.l10n_mx_edi_payment_method_id.id,
            'amount': 0 + self.amount,
        }
        operations_line = self.sudo().env['account.cash.control.operations'].create(values)
