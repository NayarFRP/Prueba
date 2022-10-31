# -*- coding: utf-8 -*-
from odoo import models, api, fields

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    ref = fields.Char(string="Referencia")
    partner_id = fields.Many2one('res.partner', string="Contacto (Ayuda en conciliación)")
    