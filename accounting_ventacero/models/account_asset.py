# -*- coding: utf-8 -*-
from odoo import models, api, fields

class AccountAsset(models.Model):
    _inherit = 'account.asset'

    lot_id = fields.Many2one('stock.production.lot', string="No de Serie")
    notes = fields.Text(string="Notas")

    def close_asset(self):
        self.update({
            'state': 'close'
        })
