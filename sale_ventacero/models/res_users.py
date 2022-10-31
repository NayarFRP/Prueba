# -*- coding: utf-8 -*-
from odoo import models, api, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    account_journal_ids = fields.Many2many('account.journal', string="Diarios de pago")
