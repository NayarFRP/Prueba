# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime


class ResPartner(models.Model):
    _inherit = 'res.partner'

    amount_credit_limit = fields.Monetary(string='Límite de crédito interno', default=-1)
    credit_limit_compute = fields.Monetary(
        string='Límite de crédito', default=-1,
        compute='_compute_credit_limit_compute', inverse='_inverse_credit_limit_compute',
        help='Un límite de cero significa que no hay límite. Un límite de -1 utilizará el límite predeterminado (empresa)'
    )
    show_credit_limit = fields.Boolean(compute='_compute_show_credit_limit')

    tipo_riesgo = fields.Selection([('bajo', 'Bajo'), ('medio', 'Medio'), ('alto', 'Alto')], string="Tipo de riesgo")
    poliza_credito = fields.Char(string="Póliza de crédito")
    comportamiento_pago = fields.Selection([('excelente', 'Excelente'), ('bueno', 'Bueno'), ('regular', 'Regular'), ('moroso', 'Moroso')], string="Comportamiento de pago")

    tipo_credito = fields.Selection([('clasificado', 'Clasificado'), ('discrecional', 'Discrecional'), ('excluido', 'Excluido'), ('sin_asegurar', 'Sin asegurar')], string="Tipo de credito")
    numero_asegurado = fields.Char(string="Número asegurado")
    limite_credito_asegurado = fields.Monetary(string="Límite de crédito asegurado")
    fecha_asegurado = fields.Date(string="Fecha asegurado")
    pagare = fields.Boolean(string="Pagaré")
    monto_pagare = fields.Monetary(string="Monto pagaré")
    siniestro = fields.Boolean(string="Siniestro")
    prorroga = fields.Boolean(string="Prorroga")

    credit_due_days = fields.Integer(string='Dias vencido', compute='_get_credit_due_days')

    risk_order = fields.Float(string="Pedidos de venta", compute='_compute_risk')
    risk_invoice_draft = fields.Float(string="Facturas borrador", compute='_compute_risk')
    risk_invoice_open = fields.Float(string="Facturas abiertas", compute='_compute_risk')
    risk_invoice_overdue = fields.Float(string="Facturas vencidas", compute='_compute_risk')
    risk_total = fields.Float(string="Riesgo total", compute='_compute_total_risk')

    risk_order_bool = fields.Boolean(string="Pedidos de venta")
    risk_invoice_draft_bool = fields.Boolean(string="Facturas borrador")
    risk_invoice_open_bool = fields.Boolean(string="Facturas abiertas")
    risk_invoice_overdue_bool = fields.Boolean(string="Facturas vencidas")


    @api.depends('amount_credit_limit')
    @api.depends_context('company')
    def _compute_credit_limit_compute(self):
        for partner in self:
            partner.credit_limit_compute = self.env.company.account_default_credit_limit if partner.amount_credit_limit == -1 else partner.amount_credit_limit

    @api.depends('credit_limit_compute')
    @api.depends_context('company')
    def _inverse_credit_limit_compute(self):
        for partner in self:
            is_default = partner.credit_limit_compute == self.env.company.account_default_credit_limit
            partner.amount_credit_limit = -1 if is_default else partner.credit_limit_compute

    @api.depends_context('company')
    def _compute_show_credit_limit(self):
        for partner in self:
            partner.show_credit_limit = self.env.company.account_credit_limit

    def _commercial_fields(self):
        return super(ResPartner, self)._commercial_fields() + ['amount_credit_limit']


    @api.depends('credit')
    def _get_credit_due_days(self):
        current_date = datetime.today().date()
        for partner in self:
            facturas_vencidas = self.env['account.move'].sudo().search([('partner_id', '=', partner.id), ('move_type', '=', 'out_invoice'), ('invoice_date_due', '<', current_date)], order='invoice_date_due ASC', limit=1)
            if len(facturas_vencidas) > 0:
                diff_date = current_date - facturas_vencidas.invoice_date_due
                partner.credit_due_days = diff_date.days
            else:
                partner.credit_due_days = 0


    @api.depends('sale_order_count', 'total_invoiced')
    def _compute_risk(self):
        current_date = datetime.today().date()
        for reg in self:
            risk_order = 0
            risk_invoice_draft = 0
            risk_invoice_open = 0
            risk_invoice_overdue = 0

            pedidos = self.env['sale.order'].sudo().search([('partner_id', '=', reg.id), ('state', 'in', ('done', 'sale')), ('invoice_ids', '=', False)])
            if pedidos:
                for order in pedidos:
                    risk_order += order.amount_total

            facturas_borrador = self.env['account.move'].sudo().search([('partner_id', '=', reg.id), ('move_type', '=', 'out_invoice'), ('state', '=', 'draft')])
            if facturas_borrador:
                for inv in facturas_borrador:
                    risk_invoice_draft += inv.amount_total_signed

            facturas_abiertas = self.env['account.move'].sudo().search([('partner_id', '=', reg.id), ('move_type', '=', 'out_invoice'), ('state', '=', 'posted'), ('invoice_date_due', '>=', current_date), ('payment_state', 'in', ('not_paid', 'partial'))])
            if facturas_abiertas:
                for inv in facturas_abiertas:
                    risk_invoice_open += inv.amount_total_signed

            facturas_vencidas = self.env['account.move'].sudo().search([('partner_id', '=', reg.id), ('move_type', '=', 'out_invoice'), ('state', '=', 'posted'), ('invoice_date_due', '<', current_date), ('payment_state', 'in', ('not_paid', 'partial'))])
            if facturas_vencidas:
                for inv in facturas_vencidas:
                    risk_invoice_overdue += inv.amount_total_signed


            reg.update({
                'risk_order': risk_order,
                'risk_invoice_draft': risk_invoice_draft,
                'risk_invoice_open': risk_invoice_open,
                'risk_invoice_overdue': risk_invoice_overdue,
            })


    @api.depends('risk_order_bool', 'risk_invoice_draft_bool', 'risk_invoice_open_bool', 'risk_invoice_overdue_bool')
    def _compute_total_risk(self):
        for reg in self:
            total = 0

            if reg.risk_order_bool:
                total += reg.risk_order
            if reg.risk_invoice_draft_bool:
                total += reg.risk_invoice_draft
            if reg.risk_invoice_open_bool:
                total += reg.risk_invoice_open
            if reg.risk_invoice_overdue_bool:
                total += reg.risk_invoice_overdue

            reg.update({
                'risk_total': total
            })
