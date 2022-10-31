# -*- coding: utf-8 -*-
from odoo import models, api, fields

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    payment_batch = fields.Boolean("Visibe en pago por lotes")
    