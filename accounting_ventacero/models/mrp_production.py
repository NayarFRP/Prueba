# -*- coding: utf-8 -*-
from odoo import models, api, fields
from datetime import datetime

class MrpProduction(models.Model):
    _inherit = 'mrp.production'


    def button_mark_done(self):
        result = super(MrpProduction, self).button_mark_done()
        currency = self.env['res.currency'].search([('name', '=', 'MXN')])
        production_ub = self.env['stock.location'].search([('usage', '=', 'production')])
        if self.state == 'done':
            for line in self.move_raw_ids:
                if line.product_id.detailed_type == 'consu':
                    cost = line.quantity_done * line.product_id.standard_price
                    move_lines = [
                                (0, 0, {
                                    'account_id' : line.product_id.categ_id.property_stock_valuation_account_id.id,
                                    'name': self.name +  ' - Maquila',
                                    'amount_currency': cost * -1,
                                    'credit': cost,
                                    'currency_id' : currency.id,
                                    
                                }),
                                (0, 0, {
                                    'account_id' : production_ub.valuation_in_account_id.id,
                                    'name': self.name +  ' - Maquila',
                                    'amount_currency': cost,
                                    'debit': cost,
                                    'currency_id' : currency.id,
                                })
                            ]
                    values = {
                        'ref' : self.name +  ' - Maquila',
                        'date' : datetime.today(),
                        'journal_id' : self.product_id.categ_id.property_stock_journal.id,
                        'line_ids' : move_lines,
                        'currency_id' : currency.id
                        }
                    asiento = self.sudo().env['account.move'].create(values)
                    asiento.action_post()
            
        return result
        