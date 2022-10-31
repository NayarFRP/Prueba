# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools, _

class AccountPayment(models.Model):
    _inherit = 'account.payment'


    @api.model
    def create(self, vals):
        result = super(AccountPayment, self).create(vals)

        if self._context.get('active_model', []) == 'hr.expense.sheet':
            informes = self.env['hr.expense.sheet'].browse(self._context.get('active_ids', []))
            if informes:
                for informe in informes:
                    informe.refund_id = result.id

        return result

    
