# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    account_credit_limit = fields.Boolean()
    account_default_credit_limit = fields.Monetary()
    credit_limit_type = fields.Selection([('warning', 'Advertencia'), ('block', 'Bloqueo')])