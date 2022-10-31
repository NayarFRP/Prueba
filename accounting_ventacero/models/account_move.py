# -*- coding: utf-8 -*-
from odoo import models, api, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    credit_note_reason_id = fields.Many2one('credit.note.reasons', string='Motivo')
    invoice_to_cancel = fields.Many2one('account.move', string="Factura a cancelar")
    replacement_invoice = fields.Many2one('account.move', string="Factura de reemplazo")

    @api.model
    def create(self, vals):
        result = super(AccountMove, self).create(vals)

        if result.move_type == 'out_invoice':
            if result.partner_id.l10n_mx_edi_payment_method_id:
                result.l10n_mx_edi_payment_method_id = result.partner_id.l10n_mx_edi_payment_method_id.id

            if result.partner_id.l10n_mx_edi_usage:
                result.l10n_mx_edi_usage = result.partner_id.l10n_mx_edi_usage

        return result


    def action_post(self):
        result = super(AccountMove, self).action_post()

        if self.partner_id.ref:
            self.payment_reference = self.partner_id.ref

        return result


    def button_replace_invoice(self):
        if self.invoice_to_cancel:
            self.invoice_to_cancel.l10n_mx_edi_origin = '04|' + self.l10n_mx_edi_cfdi_uuid
            self.invoice_to_cancel.button_cancel_posted_moves()
        else:
            values={
                'partner_id': self.partner_id.id,
                'invoice_to_cancel': self.id,
                'journal_id': self.journal_id.id,
                'currency_id': self.currency_id.id,
            }
            new_invoice = self.sudo().env['account.move'].create(values)
            self.replacement_invoice = new_invoice.id
            return {
                "type":"ir.actions.act_window",
                "res_model": "account.move",
                "views": [[False, "form"]],
                "res_id": new_invoice.id,
                "target": "current",
            }
        