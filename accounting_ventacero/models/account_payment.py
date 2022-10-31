# -*- coding: utf-8 -*-
from odoo import models, api, fields

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.model
    def create(self, vals):
        result = super(AccountPayment, self).create(vals)
        
        if result.partner_id.ref:
            result.ref = result.partner_id.ref

        if result.journal_id.ref:
            result.ref = result.journal_id.ref

        return result
