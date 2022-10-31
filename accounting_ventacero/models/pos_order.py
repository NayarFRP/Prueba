# -*- coding: utf-8 -*-
from odoo import models, api, fields

class PosOrder(models.Model):
    _inherit = 'pos.order'


    def action_pos_order_paid(self):
        """Extencion de funcion para aplicar metodo de pago al cliente dependiendo de la forma de pago utilizada"""
        res = super().action_pos_order_paid()
        payment_count = self.sudo().env['pos.payment'].search_count([('pos_order_id', '=', self.id)])
        if payment_count > 1:
            payment_method_id = self.sudo().env['l10n_mx_edi.payment.method'].search([('code', '=', '99')])
            self.partner_id.l10n_mx_edi_payment_method_id = payment_method_id.id
        else:
            for line in self.payment_ids:
                self.partner_id.l10n_mx_edi_payment_method_id = line.payment_method_id.journal_id.l10n_mx_edi_payment_method_id.id
        return res
    