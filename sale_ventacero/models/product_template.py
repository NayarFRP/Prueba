# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    equivalent_weight = fields.Float(string="Peso equivalente")
    