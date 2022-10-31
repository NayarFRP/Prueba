# -*- coding: utf-8 -*-
from odoo import models, api, fields

class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    account_type = fields.Selection([('01', 'Cuenta de cheques'), ('03', 'Cuenta de débito'), ('04', 'Cuenta de crédito'), ('05', 'Cuenta CLABE')], string="Tipo de cuenta")
    codigo_terceros = fields.Char('Codigo de terceros')
    referencia_numerica = fields.Char('Referencia numerica')
    referencia_alfanumerica = fields.Char('Referencia alfanumerica')
    descripcion_pago = fields.Char('Descripción de pago')
    descripcion_pago_2 = fields.Char('Descripción de pago 2')

    