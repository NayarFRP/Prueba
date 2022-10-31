# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools, _
import logging

_logger = logging.getLogger(__name__)

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    operation_line_id = fields.Many2one('account.cash.control.operations', string='Linea de operacion')
    balance_line_id = fields.Many2one('account.cash.control.operations', string='Linea de operacion')

    def action_post(self):
        result = super(AccountPayment, self).action_post()

        for payment in self:
            if not payment.is_internal_transfer and payment.payment_type == 'inbound':
                #AGREGA LINEA EN OPERACIONES

                caja_id = self.sudo().env['account.cash.control'].search([('team_id', '=', payment.journal_id.team_id.id), ('date', '=', payment.date)])

                values = {
                    'cash_control_id': caja_id.id,
                    'payment_id': payment.id,
                    'name': payment.name,
                    'journal_id': payment.journal_id.id,
                    'partner_id': payment.partner_id.id,
                    'l10n_mx_edi_payment_method_id': payment.l10n_mx_edi_payment_method_id.id,
                    'amount': 0 + payment.amount,
                }
                operations_line = self.sudo().env['account.cash.control.operations'].create(values)

                #TOMO ID DE LINEA DE OPERACION Y LA PONGO EN EL PAGO

                payment.operation_line_id = operations_line.id

                #SUMA VALOR EN DIARIO DE SALDOS
                balance_line_id = self.sudo().env['account.cash.control.balance'].search([('cash_control_id', '=', caja_id.id), ('journal_id', '=', payment.journal_id.id)])
                balance_line_id.update({
                    'sale_balance': balance_line_id.sale_balance + payment.amount
                })

        return result

    def action_draft(self):
        result = super(AccountPayment, self).action_draft()

        if not self.is_internal_transfer:
            #BORRO LINEA DE OPERACION
            if self.operation_line_id:
                caja_id = self.operation_line_id.cash_control_id.id
                self.operation_line_id.unlink()

                if caja_id:
                    #RESTA VALOR EN DIARIO DE SALDOS
                    balance_line_id = self.sudo().env['account.cash.control.balance'].search([('cash_control_id', '=', caja_id), ('journal_id', '=', self.journal_id.id)])
                    balance_line_id.update({
                        'sale_balance': balance_line_id.sale_balance - self.amount
                    })

        return result

    def action_cancel(self):
        result = super(AccountPayment, self).action_cancel()

        if not self.is_internal_transfer:
            #BORRO LINEA DE OPERACION
            if self.operation_line_id:
                caja_id = self.operation_line_id.cash_control_id.id
                self.operation_line_id.unlink()

                #RESTA VALOR EN DIARIO DE SALDOS
                balance_line_id = self.sudo().env['account.cash.control.balance'].search([('cash_control_id', '=', caja_id), ('journal_id', '=', self.journal_id.id)])
                balance_line_id.update({
                    'sale_balance': balance_line_id.sale_balance - self.amount
                })

        return result