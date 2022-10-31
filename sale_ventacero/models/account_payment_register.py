# -*- coding: utf-8 -*-
from odoo import models, api, fields

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    user_id = fields.Many2one('res.users', string='Usuario', default=lambda self: self.env.user)
    account_journal_ids = fields.Many2many(related='user_id.account_journal_ids')


    @api.onchange('user_id')
    def _onchange_user_id(self):
        if not self.journal_id.payment_batch:
            self.journal_id = False

    @api.onchange('journal_id')
    def _onchange_journal_id_ventacero(self):
        if self.journal_id:
            self.l10n_mx_edi_payment_method_id = self.journal_id.l10n_mx_edi_payment_method_id.id


    def _create_payment_vals_from_batch(self, batch_result):
        # OVERRIDE
        payment_vals = super()._create_payment_vals_from_batch(batch_result)
        payment_vals['l10n_mx_edi_payment_method_id'] = self.l10n_mx_edi_payment_method_id.id
        return payment_vals
