# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from datetime import date

class WizardCashControlClose(models.TransientModel):
    _name = 'wizard.cash.control.close'
    _description = 'Boton cierre de caja'

    name = fields.Char("Descripción")
    team_id = fields.Many2one('crm.team', string='Sucursal')
    journal_id = fields.Many2one('account.journal', string='Diario de deposito de efectivo')


    def b_cerrar(self):
        caja = self.sudo().env['account.cash.control'].browse(self._context.get('active_id', []))
        efectivo = self.sudo().env['account.cash.control.balance'].search([('cash_control_id', '=', caja.id), ('journal_id.type', '=', 'cash'), ('journal_id.caja_retiro', '=', False)])
        retiro = self.sudo().env['account.cash.control.balance'].search([('cash_control_id', '=', caja.id), ('journal_id.type', '=', 'cash'), ('journal_id.caja_retiro', '=', True)])


        if (caja.diference_total * -1) <= caja.team_id.max_diference:
            caja.allow_close = True

        if caja.allow_close:
            for line in caja.account_cash_control_balance_id:
                if not line.id == efectivo.id:
                    #Si es linea de caja de retiro, tomo origen la linea de efectivo
                    if line.id == retiro.id:
                        values = {
                            'is_internal_transfer': True,
                            'payment_type': 'outbound',
                            'amount': line.ending_balance,
                            'date': date.today(),
                            'ref': "Transferencia a caja de retiro",
                            'journal_id': efectivo.journal_id.id,
                            'destination_journal_id': retiro.journal_id.id,
                        }
                        transfer = self.sudo().env['account.payment'].create(values)
                        transfer.action_post()
                    else:
                        values = {
                            'is_internal_transfer': True,
                            'payment_type': 'outbound',
                            'amount': line.ending_balance,
                            'date': date.today(),
                            'ref': "Transferencia a caja de retiro",
                            'journal_id': line.journal_id.id,
                            'destination_journal_id': retiro.journal_id.id,
                        }
                        transfer = self.sudo().env['account.payment'].create(values)
                        transfer.action_post()

            for line in caja.account_cash_control_balance_id:
                if not line.id == efectivo.id:
                    #Si es linea de caja de retiro, tomo como destino el diario seleccionado
                    if line.id == retiro.id:
                        values = {
                            'is_internal_transfer': True,
                            'payment_type': 'outbound',
                            'amount': line.ending_balance,
                            'date': date.today(),
                            'ref': "Transferencia a " + str(self.journal_id.name),
                            'journal_id': retiro.journal_id.id,
                            'destination_journal_id': self.journal_id.id,
                        }
                        transfer = self.sudo().env['account.payment'].create(values)
                        transfer.action_post()
                    else:
                        #Todo como destino el diario de deposito del diario lol
                        values = {
                            'is_internal_transfer': True,
                            'payment_type': 'outbound',
                            'amount': line.ending_balance,
                            'date': date.today(),
                            'ref': "Transferencia a " + str(line.journal_id.deposit_journal.name),
                            'journal_id': retiro.journal_id.id,
                            'destination_journal_id': line.journal_id.deposit_journal.id,
                        }
                        transfer = self.sudo().env['account.payment'].create(values)
                        transfer.action_post()

        else:
            raise ValidationError(_("Excede la diferencia permitida"))

        caja.update({
            'date_end': datetime.today(),
            'state': 'close',
        })
