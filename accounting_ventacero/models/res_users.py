# -*- coding: utf-8 -*-
from odoo import models, api, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    account_analytic_account_ids = fields.Many2many('account.analytic.account', string="Cuentas analíticas")
    account_analytic_tag_ids = fields.Many2many('account.analytic.tag', string="Etiquetas analíticas")
    