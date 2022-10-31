# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
import base64
import logging

_logger = logging.getLogger(__name__)


class AccountPaymentBatch(models.Model):
    _name = 'account.payment.batch'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin', 'avatar.mixin']
    _description = 'Lote de pago'

    name = fields.Char('Nombre', copy=False, index=True, default=lambda self: _('New'))
    state = fields.Selection([
        ('draft', 'Nuevo'),
        ('confirmed', 'Confirmado'),
        ('generated', 'Generado'),
        ('uploaded', 'Cargado/Depositado'),
        ('done', 'Finalizado'),
        ('cancel', 'Cancelado')
    ], string='Estado', tracking=True, default='draft')
    payment_mode = fields.Selection([
        ('transfer', 'Transferencia electrónica'),
        ('check', 'Cheque')
    ], string='Modo de pago', default='trasferencia')
    journal_id = fields.Many2one('account.journal', string="Banco")
    payment_type = fields.Selection([
        ('invoice', 'Facturas'),
        ('account', 'Cuenta')
    ], string='Tipo de pago', default='invoice')
    ref = fields.Char('No. cheque', copy=False, index=True, default=lambda self: _('New'))
    partner_id = fields.Many2one('res.partner', string="Proveedor")
    account_id = fields.Many2one('account.account', string="Cuenta contable")
    date = fields.Date('Fecha', default=datetime.today())
    user_id = fields.Many2one('res.users', string="Usuario", default=lambda self: self.env.user)
    add_leyenda = fields.Boolean("Agregar leyenda")
    leyenda = fields.Char("Leyenda", default="Para abono en cuenta del beneficiario")

    partner_name = fields.Char('Nombre en cheque')
    payment_amount = fields.Float('Monto')
    
    account_move_ids = fields.Many2many('account.move')
    payment_batch_line_ids = fields.One2many('account.payment.batch.line', 'payment_batch_id', string="Lineas de pago")
    amount_total = fields.Float('Total', compute='_compute_amount_total')


    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].sudo().next_by_code('account.payment.batch') or _('New')

        if vals.get('payment_mode') == 'check':
            if vals.get('ref', _('New')) == _('New'):

                codigo_banco = self.env['account.journal'].sudo().search([('id', '=', vals.get('journal_id'))]).bank_id.l10n_mx_edi_code

                if codigo_banco:
                    if codigo_banco == '002':
                        vals['ref'] = self.env['ir.sequence'].sudo().next_by_code('account.payment.batch.check.002') or _('New')
                    elif codigo_banco == '058':
                        vals['ref'] = self.env['ir.sequence'].sudo().next_by_code('account.payment.batch.check.058') or _('New')

        result = super(AccountPaymentBatch, self).create(vals)
        
        return result


    @api.depends('payment_batch_line_ids')
    def _compute_amount_total(self):
        total = 0
        for reg in self:
            for line in reg.payment_batch_line_ids:
                total += line.amount

            reg.update({
                'amount_total': round(total, 2),
            })


    def _compute_payment_ids(self):
        for reg in self:
            payment_count = reg.env['account.payment'].search_count([('payment_batch_id', '=', reg.id)])
            reg.update({
                'payment_count': payment_count,
            })

    payment_count = fields.Integer(string='Receptions count', compute='_compute_payment_ids')
    payment_ids = fields.One2many('account.payment', 'payment_batch_id', string='Pagos')

    def action_view_payments(self):
        self.ensure_one()
        pagos = self.mapped('payment_ids')

        if len(pagos) > 1:
            action = self.env.ref('account.action_account_payments_payable').read()[0]
            action['domain'] = [('id', 'in', pagos.ids)]
            action['context'] = {"create": False}
            return action
        elif pagos:
            return {
                "type": "ir.actions.act_window",
                "res_model": "account.payment",
                "views": [[False, "form"]],
                "res_id": pagos.id,
                "context": {"create": False},
            }

    def action_confirm(self):
        if self.payment_type == 'invoice':
            for line in self.account_move_ids:
                line.payment_batch_id = self.id
                linea_pago = self.env['account.payment.batch.line'].sudo().search([('payment_batch_id', '=', self.id), ('partner_id', '=', line.partner_id.id)])

                if linea_pago:
                    linea_pago.amount += line.amount_residual_signed * -1
                    linea_pago.write({'account_move_ids': [(4, line.id)]})
                else:
                    cuenta_bancaria = self.env['res.partner.bank'].sudo().search([('partner_id', '=', line.partner_id.id)])
                    if self.payment_mode == 'transfer':
                        if not cuenta_bancaria:
                            raise ValidationError(_('Se requiere cuenta bancaria para ' + str(line.partner_id.name)))

                    values = {
                        'payment_batch_id': self.id,
                        'partner_id': line.partner_id.id,
                        'ref': line.partner_id.ref,
                        'bank_account_id': cuenta_bancaria[0].id if cuenta_bancaria else False,
                        'date': self.date,
                        'amount': line.amount_residual_signed * -1,
                        'currency_id': line.company_currency_id.id,
                        'amount_tax': line.amount_tax_signed * -1,
                        
                    }
                    linea_pago = self.env['account.payment.batch.line'].sudo().create(values)
                    linea_pago.write({'account_move_ids': [(4, line.id)]})
        elif self.payment_type == 'account':
            partner_id = self.sudo().env['res.partner'].search([('barcode', '=', 'CHEQUE')])
            currency_id = self.sudo().env['res.currency'].search([('name', '=', 'MXN')])
            if not partner_id:
                raise ValidationError(_('No se encontro contacto con codigo de barras CHEQUE'))
            values = {
                'payment_batch_id': self.id,
                'partner_id': partner_id[0].id,
                'date': self.date,
                'amount': self.payment_amount,
                'currency_id': currency_id[0].id,
            }
            linea_pago = self.env['account.payment.batch.line'].sudo().create(values)

        self.update({
                'state': 'confirmed'
            })
            
    
    def get_002_file(self):
        file = ""
        contador_pago = 1
        total_pagos = 0
        for line in self.payment_batch_line_ids:
            #1-3 = Tipo de registro (Siempre PAY)
            file = file + "PAY"

            #4-6 = Codigo de pais de cliente (Siempre 485)
            file = file + "485"

            #7-16 = 10 espacios en blanco
            file = file + "          "

            #17-22 = Fecha de transaccion (Formato AAMMDD)
            year = str(self.date.year)
            month = "0" + str(self.date.month)
            day = "0" + str(self.date.day)
            file = file + year[2:]
            file = file + month[-2:]
            file = file + day[-2:]

            #23-25 = Codigo de transaccion (072:BANAMEX, 001:OTROS BANCOS)
            codigo = "072" if line.bank_account_id.bank_id.l10n_mx_edi_code == "002" else "001"
            file = file + codigo

            #26-40 = Referencia de la transaccion (Referencia del proveedor)
            aux_ref = line.ref

            ref = ""
            if aux_ref:
                characters = "!#$%/()=?¡¨*[];:_'¿´+,><°|@¬\~`^ñ"
                for x in range(len(characters)):
                    aux_ref = aux_ref.replace(characters[x],"")

                if len(aux_ref) > 15:
                    ref = aux_ref[:15]
                elif len(aux_ref) < 15:
                    cont = 15 - len(aux_ref)
                    ref = aux_ref
                    for n in range(cont):
                        ref = ref + " "
                else:
                    ref = aux_ref
            else:
                raise ValidationError(_('Se requiere referencia para ' + str(line.partner_id.name)))
            file = file + ref

            #41-48 = Secuencia de la transaccion (Consecutivo de linea)
            cont = 8 - len(str(contador_pago))
            for n in range(cont):
                file = file + "0"
            file = file + str(contador_pago)
            contador_pago += 1

            #49-68 = RFC del beneficiario (RFC del proveedor)
            aux_rfc = line.partner_id.vat

            rfc = ""
            if aux_rfc:
                characters = "!#$%/()=?¡¨*[];:_'¿´+,.><°|@¬\~`^ñ"
                for x in range(len(characters)):
                    aux_rfc = aux_rfc.replace(characters[x],"")

                if len(aux_rfc) > 20:
                    rfc = aux_rfc[:20]
                elif len(aux_rfc) < 20:
                    cont = 20 - len(aux_rfc)
                    rfc = aux_rfc
                    for n in range(cont):
                        rfc = rfc + " "
                else:
                    rfc = aux_rfc
            else:
                raise ValidationError(_('Se requiere RFC para ' + str(line.partner_id.name)))
            file = file + rfc

            #69-71 = Moneda (Siempre MXN)
            file = file + "MXN"

            #72-91 = Codigo del beneficiario (Codigo de terceros)
            aux_ref = line.bank_account_id.codigo_terceros

            ref = ""
            if aux_ref:
                characters = "!#$%&=¡¨*[];_¿´><°|@¬\~`^ñ"
                for x in range(len(characters)):
                    aux_ref = aux_ref.replace(characters[x],"")

                if len(aux_ref) > 20:
                    ref = aux_ref[:20]
                elif len(aux_ref) < 20:
                    cont = 20 - len(aux_ref)
                    ref = aux_ref
                    for n in range(cont):
                        ref = ref + " "
                else:
                    ref = aux_ref
            else:
                ref = '                    '
            file = file + ref

            #92-106 = Importe de la transaccion (Sin puntos, comas ni nada 1,500.00 : 150000)
            monto_aux = round(line.amount, 2)
            total_pagos += monto_aux

            indice_punto = str(monto_aux).index('.')

            str_entero = str(monto_aux)[:indice_punto]
            str_decimal = str(monto_aux)[indice_punto+1:]
        
            if len(str_decimal) == 1:
                str_decimal = str_decimal + "0"
            monto = str_entero + str_decimal

            cont = 15 - len(monto)
            for n in range(cont):
                file = file + "0"
            file = file + monto

            #107-112 = Maturuty date (Siempre dejar en blanco)
            file = file + "      "

            #113-147 = Detalle de la transaccion (Referencia numerica)
            aux_ref = line.bank_account_id.referencia_numerica

            ref = ""
            if aux_ref:
                characters = "!$%&/()=?¡¨*[];:_'¿´+,.-><°|@¬\~`^ñ"
                for x in range(len(characters)):
                    aux_ref = aux_ref.replace(characters[x],"")

                if len(aux_ref) > 35:
                    ref = aux_ref[:35]
                elif len(aux_ref) < 35:
                    cont = 35 - len(aux_ref)
                    ref = aux_ref
                    for n in range(cont):
                        ref = ref + " "
                else:
                    ref = aux_ref
            else:
                ref = '                                   '
            file = file + ref

            #148-182 = Detalle de la transaccion 2 (Referencia alfanumerica)
            aux_ref = line.bank_account_id.referencia_alfanumerica

            ref = ""
            if aux_ref:
                characters = "!$%&/()=?¡¨*[];:_'¿´+,.-><°|@¬\~`^ñ"
                for x in range(len(characters)):
                    aux_ref = aux_ref.replace(characters[x],"")

                if len(aux_ref) > 35:
                    ref = aux_ref[:35]
                elif len(aux_ref) < 35:
                    cont = 35 - len(aux_ref)
                    ref = aux_ref
                    for n in range(cont):
                        ref = ref + " "
                else:
                    ref = aux_ref
            else:
                ref = '                                   '
            file = file + ref

            #183-217 = Detalle de la transaccion 3 (Descripcion de pago)
            aux_ref = line.bank_account_id.descripcion_pago

            ref = ""
            if aux_ref:
                characters = "!$%&/()=?¡¨*[];:_'¿´+,.-><°|@¬\~`^ñ"
                for x in range(len(characters)):
                    aux_ref = aux_ref.replace(characters[x],"")

                if len(aux_ref) > 35:
                    ref = aux_ref[:35]
                elif len(aux_ref) < 35:
                    cont = 35 - len(aux_ref)
                    ref = aux_ref
                    for n in range(cont):
                        ref = ref + " "
                else:
                    ref = aux_ref
            else:
                ref = '                                   '
            file = file + ref

            #218-252 = Detalle de la transaccion 4 (Descripcion de pago 2)
            aux_ref = line.bank_account_id.descripcion_pago_2

            ref = ""
            if aux_ref:
                characters = "!$%&/()=?¡¨*[];:_'¿´+,.-><°|@¬\~`^ñ"
                for x in range(len(characters)):
                    aux_ref = aux_ref.replace(characters[x],"")

                if len(aux_ref) > 35:
                    ref = aux_ref[:35]
                elif len(aux_ref) < 35:
                    cont = 35 - len(aux_ref)
                    ref = aux_ref
                    for n in range(cont):
                        ref = ref + " "
                else:
                    ref = aux_ref
            else:
                ref = '                                   '
            file = file + ref
            #253-254 = Codigo de transaccion local (Siempre 06)
            file = file + "06"

            #255-256 = Tipo de cuenta del cliente (Siempre 01)
            file = file + "01"

            #257-336 = Nombre del beneficiario (Nombre del titular de la cuenta)
            aux_ref = line.bank_account_id.acc_holder_name

            characters = "!#$%/()=?¡¨*[];:_¿´+,.-><°|@¬\~`^"
            for x in range(len(characters)):
                aux_ref = aux_ref.replace(characters[x],"")

            ref = ""
            if len(aux_ref) > 35:
                ref = aux_ref[:35]
            elif len(aux_ref) < 35:
                cont = 35 - len(aux_ref)
                ref = aux_ref
                for n in range(cont):
                    ref = ref + " "
            else:
                ref = aux_ref
            file = file + ref + "                                             "

            #337-371 = Direccion beneficiario 1 (Calle y numero de proveedor)
            aux_direccion = str(line.partner_id.street_name) + " " + str(line.partner_id.street_number)

            characters = "!#$%()=?¡¨*[];:_¿´+.-><°|¬\~`^"
            for x in range(len(characters)):
                aux_direccion = aux_direccion.replace(characters[x],"")

            direccion = ""
            if len(aux_direccion) > 35:
                direccion = aux_direccion[:35]
            elif len(aux_direccion) < 35:
                cont = 35 - len(aux_direccion)
                direccion = aux_direccion
                for n in range(cont):
                    direccion = direccion + " "
            else:
                direccion = aux_direccion
            file = file + direccion

            #372-406 = Direccion beneficiario 2 (Colonia del proveedor)
            aux_direccion = str(line.partner_id.l10n_mx_edi_colony)

            direccion = ""
            if aux_direccion:
                characters = "!#$%()=?¡¨*[];:_¿´+.-><°|¬\~`^"
                for x in range(len(characters)):
                    aux_direccion = aux_direccion.replace(characters[x],"")

                if len(aux_direccion) > 35:
                    direccion = aux_direccion[:35]
                elif len(aux_direccion) < 35:
                    cont = 35 - len(aux_direccion)
                    direccion = aux_direccion
                    for n in range(cont):
                        direccion = direccion + " "
                else:
                    direccion = aux_direccion
            else:
                direccion = "                                   "
            file = file + direccion

            #407-421 = 15 espacios en blanco
            file = file + "               "

            #422-423 = 2 espacios en blanco
            file = file + "  "

            #424-435 = 12 espacios en blanco
            file = file + "            "

            #436-451 = 16 espacios en blanco
            file = file + "                "

            #452-454 = Codigo del banco beneficiario (Banamex = 000, Codigo de banco = Transferencia)
            codigo_banco = "000" if line.bank_account_id.bank_id.l10n_mx_edi_code == "002" else str(line.bank_account_id.bank_id.l10n_mx_edi_code)
            file = file + codigo_banco

            #455-462 = 8 espacios en blanco
            file = file + "        "

            #463-497 = Numero de cuenta de beneficiario
            cuenta = str(line.bank_account_id.acc_number) if line.bank_account_id.account_type != '05' else str(line.bank_account_id.l10n_mx_edi_clabe)

            file = file + cuenta

            cont = 35 - len(cuenta)
            for n in range(cont):
                file = file + " "

            #498-499 = Tipo de cuenta de beneficiario (01=cheques, 03=debito, 04=credito, 05=clabe)
            tipo_cuenta = line.bank_account_id.account_type
            if not tipo_cuenta :
                raise ValidationError(_('Se requiere seleccionar tipo de cuenta para ' + str(line.partner_id.name)))
            file = file + str(tipo_cuenta)

            #500-529 = Direccion del banco
            aux_ref = line.bank_account_id.bank_id.name
            ref = ""
            if len(aux_ref) > 30:
                ref = aux_ref[:30]
            elif len(aux_ref) < 30:
                cont = 30 - len(aux_ref)
                ref = aux_ref
                for n in range(cont):
                    ref = ref + " "
            else:
                ref = aux_ref
            file = file + ref

            #530-546 = Importe del impuesto
            file = file + "00000000000000000"

            #547-547 = Bandera de prioridad (Si = Y, No = N)
            file = file + "N"

            #548-548 = Confidencial (Si = Y, No = N)
            file = file + "N"

            #549-550 = Fecha de acreditacion al beneficiario
            codigo = "  " if line.bank_account_id.bank_id.l10n_mx_edi_code == "002" else "01"
            file = file + codigo

            #551-570 = Numero de cuenta de debito banamex (Cuenta de la empresa)
            cuenta = self.journal_id.bank_account_id.acc_number

            file = file + "0" + cuenta

            cont = 20 - len(cuenta)
            for n in range(cont):
                file = file + " "

            #571-586 = 16 espacios en blanco
            file = file + "                "

            #587-606 = 20 espacios en blanco
            file = file + "                    "

            #607-621 = 15 espacios en blanco
            file = file + "               "

            #622-631 = 10 espacios en blanco
            file = file + "          "

            #632-633 = 2 espacios en blanco
            file = file + "  "

            #634-636 = 3 espacios en blanco
            file = file + "   "

            #637-686 = 50 espacios en blanco
            file = file + "                                                  "

            #687-691 = 5 ceros
            file = file + "00000"

            #692-741 = Correo electronico del beneficiario
            aux_correo = line.partner_id.email
            correo = ""
            if aux_correo:
                characters = "!#$%&/()=?¡¨*[];:'¿´+,><°|¬\~`^ñ"
                for x in range(len(characters)):
                    aux_correo = aux_correo.replace(characters[x],"")

                if len(aux_correo) > 50:
                    correo = aux_correo[:50]
                elif len(aux_correo) < 50:
                    cont = 50 - len(aux_correo)
                    correo = aux_correo
                    for n in range(cont):
                        correo = correo + " "
                else:
                    correo = aux_correo
            else:
                correo = "                                                  "
            file = file + correo

            #742-756 = Importe maximo por pago (15 nueves)
            file = file + "999999999999999"

            #757-757 = 1 espacio en blanco
            file = file + " "

            #758-768 = NONE si no hay correo E-MAIL si hay correo
            aux_palabra = "E-Mail" if line.partner_id.email else "NONE"
            palabra = ""
            if len(aux_palabra) > 11:
                palabra = aux_palabra[:11]
            elif len(aux_palabra) < 11:
                cont = 11 - len(aux_palabra)
                palabra = aux_palabra
                for n in range(cont):
                    palabra = palabra + " "
            else:
                palabra = aux_palabra
            file = file + palabra

            #769-769 = 1 espacio en blanco
            file = file + " "

            #770-770 = 1 espacio en blanco
            file = file + " "

            #771 = 253 espacios en blanco
            for n in range(253):
                file = file + " "

            file = file + "\n"
        
        #Totales
        #1-3 = Tipo de registro (Siempre TRL)
        file = file + "TRL"
        
        #4-18 = Numero de transacciones
        transacciones = contador_pago - 1
        cont = 15 - len(str(transacciones))
        file = file + str(transacciones)
        for n in range(cont):
            file = file + " "
        
        #19-33 = Suma de todos los importes del registro de pagos
        monto_aux = round(total_pagos, 2)

        indice_punto = str(monto_aux).index('.')

        str_entero = str(monto_aux)[:indice_punto]
        str_decimal = str(monto_aux)[indice_punto+1:]
    
        if len(str_decimal) == 1:
            str_decimal = str_decimal + "0"
        monto = str_entero + str_decimal

        cont = 15 - len(monto)
        for n in range(cont):
            file = file + "0"
        file = file + monto

        #34-48 = 15 ceros
        file = file + "000000000000000"

        #49-63 = Numero total de registros a transmitir
        transacciones = contador_pago - 1
        cont = 15 - len(str(transacciones))
        file = file + str(transacciones)
        for n in range(cont):
            file = file + " "
        
        #64 = 37 espacios en blanco
        file = file + "                                     "

        return file


    def get_058_file(self):
        file = ""
        contador_pago = 1
        total_pagos = 0

        for line in self.payment_batch_line_ids:
            #Secuencia (5)
            cont = 5 - len(str(contador_pago))
            for n in range(cont):
                file = file + "0"
            file = file + str(contador_pago) + ","
            contador_pago += 1

            #Tipo (1) = B:Banregio, T:TEF, S:SPEI
            tipo = "B" if line.bank_account_id.bank_id.l10n_mx_edi_code == "058" else "S"
            file = file + tipo + ","

            #Cuenta destino (20)
            cuenta = str(line.bank_account_id.acc_number) if line.bank_account_id.account_type != '05' else str(line.bank_account_id.l10n_mx_edi_clabe)
            cont = 20 - len(cuenta)
            for n in range(cont):
                file = file + " "
            file = file + cuenta
            file = file + ","

            #Importe (13.2)
            monto_aux = round(line.amount, 2)

            entero = monto_aux // 1
            decimal = str(monto_aux)

            str_entero = str(entero).replace('.0', '')
            str_decimal = decimal.replace(str_entero, '')
        
            if len(str_decimal) == 2:
                str_decimal = str_decimal + "0"

            cont = 13 - len(str_entero)
            for n in range(cont):
                file = file + "0"
            file = file + str_entero + str_decimal + ","

            #IVA (16)
            monto_aux = str(round(line.amount_tax, 2))

            indice_punto = monto_aux.index('.')

            str_entero = monto_aux[:indice_punto]
            str_decimal = monto_aux[indice_punto+1:]
          
            if len(str_decimal) == 1:
                str_decimal = str_decimal + "0"
            monto = str_entero + "." + str_decimal

            cont = 16 - len(monto)
            for n in range(cont):
                file = file + "0"
            file = file + monto + ","

            #Descripcion (40)
            aux_ref = line.bank_account_id.referencia_alfanumerica
            ref = ""
            if aux_ref:
                if len(aux_ref) > 40:
                    ref = aux_ref[:40]
                elif len(aux_ref) < 40:
                    cont = 40 - len(aux_ref)
                    for n in range(cont):
                        ref = ref + " "
                    ref = ref + aux_ref
                else:
                    ref = aux_ref
            else:
                raise ValidationError(_('Se requiere referencia para ' + str(line.partner_id.name)))
            file = file + ref + ","

            #Ref_Numerica (15)
            aux_ref = str(line.bank_account_id.referencia_numerica)
            ref = ""
            if aux_ref:
                if len(aux_ref) > 15:
                    ref = aux_ref[:15]
                elif len(aux_ref) < 15:
                    cont = 15 - len(aux_ref)
                    for n in range(cont):
                        ref = ref + " "
                    ref = ref + aux_ref
                else:
                    ref = aux_ref
            else:
                raise ValidationError(_('Se requiere referencia para ' + str(line.partner_id.name)))
            file = file + ref
            
            file = file + "\n"
        return file


    def action_generate_file(self):
        codigo_banco = self.journal_id.bank_id.l10n_mx_edi_code
        if codigo_banco:
            if codigo_banco == '002':
                file_data = self.get_002_file()
            elif codigo_banco == '058':
                file_data = self.get_058_file()

            values = {
                'name': str(self.name) + '.txt',
                'store_fname': str(self.name) + '.txt',
                'res_model': 'account.payment.batch',
                'res_id': self.id,
                'type': 'binary',
                'public': True,
                'datas': base64.b64encode(str.encode(file_data))
            }
            attachment_id = self.env['ir.attachment'].sudo().create(values)
            download_url = '/web/content/' + str(attachment_id.id) + '?download=True'
            base_url = self.env['ir.config_parameter'].get_param('web.base.url')

            self.update({
                'state': 'generated'
            })

            return {       
                "type": "ir.actions.act_url",       
                "url": str(base_url)  +  str(download_url),      
                "target": "new",    
            }
        else:
            pass


    def action_generate_check(self):
        codigo_banco = self.journal_id.bank_id.l10n_mx_edi_code
        if codigo_banco:
            if codigo_banco == '002':
                self.update({
                    'state': 'generated'
                })
                return self.env.ref('payment_ventacero.report_account_payment_batch_002').report_action(self)
            elif codigo_banco == '058':
                self.update({
                    'state': 'generated'
                })
                return self.env.ref('payment_ventacero.report_account_payment_batch_058').report_action(self)
        else:
            pass


    def action_file_uploaded(self):
        self.update({
            'state': 'uploaded'
        })

    def action_check_deposited(self):
        self.update({
            'state': 'uploaded'
        })

    def action_done(self):
        self.update({
            'state': 'done'
        })
        if self.payment_type == 'invoice':
            return {
                'name': _('Register Payment'),
                'res_model': 'account.payment.register',
                'view_mode': 'form',
                'context': {
                    'active_model': 'account.move',
                    'active_ids': self.account_move_ids.ids,
                    'default_journal_id': self.journal_id.id,
                    'default_l10n_mx_edi_payment_method_id': self.journal_id.l10n_mx_edi_payment_method_id.id,
                    'default_group_payment': True
                },
                'target': 'new',
                'type': 'ir.actions.act_window',
            }
        else:
            partner_id = self.sudo().env['res.partner'].search([('barcode', '=', 'CHEQUE')])
            partner_id.property_account_payable_id = self.account_id.id

            return {
                'res_model': 'account.payment',
                'view_mode': 'form',
                'context': {
                    'default_payment_type': 'outbound',
                    'default_partner_type': 'supplier',
                    'default_amount': self.amount_total,
                    'default_ref': self.name,
                    'default_id_payment_batch': self.id,
                    'default_journal_id': self.journal_id.id,
                    'default_l10n_mx_edi_payment_method_id': self.journal_id.l10n_mx_edi_payment_method_id.id,
                    'default_group_payment': True,
                    'default_partner_id': partner_id.id
                },
                'target': 'new',
                'type': 'ir.actions.act_window',
            }
        
    def action_new(self):
        if self.payment_count > 0:
            for line in self.payment_ids:
                line.action_draft()
                line.unlink()

        self.update({
            'state': 'draft',
            'payment_batch_line_ids':[(6,0,[])]
        })

    def action_cancel(self):
        self.update({
            'state': 'cancel'
        })


    def get_fecha(self):
        fecha = str(self.date)
        str_mes = ''

        dia = fecha[8:10]
        mes = fecha[5:7]
        anio = fecha[0:4]

        if mes == '01':
            str_mes = 'Enero'
        elif mes == '02':
            str_mes = 'Febrero'
        elif mes == '03':
            str_mes = 'Marzo'
        elif mes == '04':
            str_mes = 'Abril'
        elif mes == '05':
            str_mes = 'Mayo'
        elif mes == '06':
            str_mes = 'Junio'
        elif mes == '07':
            str_mes = 'Julio'
        elif mes == '08':
            str_mes = 'Agosto'
        elif mes == '09':
            str_mes = 'Septiembre'
        elif mes == '10':
            str_mes = 'Octubre'
        elif mes == '11':
            str_mes = 'Noviembre'
        elif mes == '12':
            str_mes = 'Diciembre'

        return dia + " " + str_mes + " " + anio


    def get_monto_texto(self):
        self.ensure_one()
        currency_name = 'MXN'
        # M.N. = Moneda Nacional (National Currency)
        # M.E. = Moneda Extranjera (Foreign Currency)
        currency_type = 'M.N' if currency_name == 'MXN' else 'M.E.'
        currency_id = self.sudo().env['res.currency'].search([('name', '=', 'MXN')])

        # Split integer and decimal part
        amount_i, amount_d = divmod(self.amount_total, 1)
        amount_d = round(amount_d, 2)
        amount_d = int(round(amount_d * 100, 2))

        words = currency_id.with_context(lang=self.partner_id.lang or 'es_ES').amount_to_text(amount_i).upper()
        return '%(words)s %(amount_d)02d/100 %(currency_type)s' % {
            'words': words,
            'amount_d': amount_d,
            'currency_type': currency_type,
        }

    def get_leyenda(self):
        for reg in self:
            if reg.add_leyenda:
                return reg.leyenda
            else:
                return ''

