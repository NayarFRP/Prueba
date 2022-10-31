# -*- coding: utf-8 -*-
from odoo import models, fields, Command, api, tools, _

class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    name = fields.Text(string='Descripción')

    @api.onchange('product_id')
    def onchange_product_id_ventacero(self):
        if not self.product_id:
            self.name = ''
        else:
            self.name = self.product_id.name
            