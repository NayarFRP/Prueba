# -*- coding: utf-8 -*-
from odoo import models, fields, Command, api, tools, _
from odoo.tools.float_utils import float_repr
from lxml import etree
from lxml.objectify import fromstring
import base64
import logging

_logger = logging.getLogger(__name__)

CFDI_XSLT_CADENA = 'l10n_mx_edi/data/3.3/cadenaoriginal.xslt'
CFDI_XSLT_CADENA_TFD = 'l10n_mx_edi/data/xslt/3.3/cadenaoriginal_TFD_1_1.xslt'


class HrExpense(models.Model):
    _inherit = 'hr.expense'

    l10n_mx_edi_cfdi_uuid = fields.Char(string='Folio Fiscal', copy=False, readonly=True,
        help='Folio in electronic invoice, is returned by SAT when send to stamp.')
    supplier_id = fields.Many2one('res.partner', string='Proveedor')
    payment_mode = fields.Selection(selection_add=[('petty_cash', 'Fondo Fijo')], default='petty_cash')

    subtotal_gasto = fields.Float('Subtotal')
    importe_impuesto = fields.Float('Impuesto (Importe)')
    impuesto_tag = fields.Many2one('account.tax', string='Impuesto')

    def _l10n_mx_edi_get_cadena_xslts(self):
        return CFDI_XSLT_CADENA_TFD, CFDI_XSLT_CADENA

    def _get_l10n_mx_edi_cfdi_attachment(self):
        self.ensure_one()
        attachment = False
        if not self.l10n_mx_edi_cfdi_uuid:
            attachment = self.env['ir.attachment'].search([('mimetype', '=', 'application/xml'), ('res_model', '=', 'hr.expense'), ('res_id', '=', self.id)], limit=1, order='create_date desc')
        return attachment

    def _l10n_mx_edi_decode_cfdi(self, cfdi_data=None):
        ''' Helper to extract relevant data from the CFDI to be used, for example, when printing the invoice.
        :param cfdi_data:   The optional cfdi data.
        :return:            A python dictionary.
        '''
        self.ensure_one()

        def get_node(cfdi_node, attribute, namespaces):
            if hasattr(cfdi_node, 'Complemento'):
                node = cfdi_node.Complemento.xpath(attribute, namespaces=namespaces)
                return node[0] if node else None
            else:
                return None

        def get_cadena(cfdi_node, template):
            if cfdi_node is None:
                return None
            cadena_root = etree.parse(tools.file_open(template))
            return str(etree.XSLT(cadena_root)(cfdi_node))

        # Find a signed cfdi.
        if not cfdi_data:      
            attachment = self._get_l10n_mx_edi_cfdi_attachment()
            if attachment:
                cfdi_data = base64.decodebytes(attachment.with_context(bin_size=False).datas)

        # Nothing to decode.
        if not cfdi_data:
            return {}

        try:
            cfdi_node = fromstring(cfdi_data)
            emisor_node = cfdi_node.Emisor
            receptor_node = cfdi_node.Receptor
            impuestos_node = cfdi_node.Impuestos.Traslados
        except etree.XMLSyntaxError:
            # Not an xml
            return {}
        except AttributeError:
            # Not a CFDI
            return {}

        tfd_node = get_node(
            cfdi_node,
            'tfd:TimbreFiscalDigital[1]',
            {'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'},
        )

        return {
            'uuid': ({} if tfd_node is None else tfd_node).get('UUID'),
            'supplier_rfc': emisor_node.get('Rfc', emisor_node.get('rfc')),
            'customer_rfc': receptor_node.get('Rfc', receptor_node.get('rfc')),
            'serie': cfdi_node.get('Serie', cfdi_node.get('serie')),
            'folio': cfdi_node.get('Folio', cfdi_node.get('folio')),
            'subtotal': cfdi_node.get('SubTotal', cfdi_node.get('subtotal')),
            'amount_total': cfdi_node.get('Total', cfdi_node.get('total')),
            'impuestos':impuestos_node,
            'cfdi_node': cfdi_node,
            'usage': receptor_node.get('UsoCFDI'),
            'payment_method': cfdi_node.get('formaDePago', cfdi_node.get('MetodoPago')),
            'bank_account': cfdi_node.get('NumCtaPago'),
            'sello': cfdi_node.get('sello', cfdi_node.get('Sello', 'No identificado')),
            'sello_sat': tfd_node is not None and tfd_node.get('selloSAT', tfd_node.get('SelloSAT', 'No identificado')),
            'cadena': tfd_node is not None and get_cadena(tfd_node, self._l10n_mx_edi_get_cadena_xslts()[0]) or get_cadena(cfdi_node, self._l10n_mx_edi_get_cadena_xslts()[1]),
            'certificate_number': cfdi_node.get('noCertificado', cfdi_node.get('NoCertificado')),
            'certificate_sat_number': tfd_node is not None and tfd_node.get('NoCertificadoSAT'),
            'expedition': cfdi_node.get('LugarExpedicion'),
            'fiscal_regime': emisor_node.get('RegimenFiscal', ''),
            'emission_date_str': cfdi_node.get('fecha', cfdi_node.get('Fecha', '')).replace('T', ' '),
            'stamp_date': tfd_node is not None and tfd_node.get('FechaTimbrado', '').replace('T', ' '),
        }

    def compute_cfdi_values(self):
        for move in self:
            #CAMPOS DE XML
            cfdi_infos = move._l10n_mx_edi_decode_cfdi()
            move.l10n_mx_edi_cfdi_uuid = cfdi_infos.get('uuid')
            move.total_amount = cfdi_infos.get('amount_total')
            move.subtotal_gasto = cfdi_infos.get('subtotal')
            move.reference = str(cfdi_infos.get('serie')) + "/" + str(cfdi_infos.get('folio'))

            #CUENTA Y ETIQUETA ANALITICA
            regla = self.sudo().env['account.analytic.default'].search([('user_id', '=', self.env.user.id)])
            move.analytic_account_id = regla.analytic_id.id
            move.analytic_tag_ids = regla.analytic_tag_ids

    def _get_default_expense_sheet_values(self):
        if any(expense.state != 'draft' or expense.sheet_id for expense in self):
            raise UserError(_("You cannot report twice the same line!"))
        if len(self.mapped('employee_id')) != 1:
            raise UserError(_("You cannot report expenses for different employees in the same report."))
        if any(not expense.product_id for expense in self):
            raise UserError(_("You can not create report without category."))

        todo = self.filtered(lambda x: x.payment_mode=='own_account') or self.filtered(lambda x: x.payment_mode=='company_account') or self.filtered(lambda x: x.payment_mode=='petty_cash')
        if len(todo) == 1:
            expense_name = todo.name
        else:
            dates = todo.mapped('date')
            min_date = format_date(self.env, min(dates))
            max_date = format_date(self.env, max(dates))
            expense_name = min_date if max_date == min_date else "%s - %s" % (min_date, max_date)

        values = {
            'default_company_id': self.company_id.id,
            'default_employee_id': self[0].employee_id.id,
            'default_name': expense_name,
            'default_expense_line_ids': [Command.set(todo.ids)],
            'default_state': 'draft',
            'create': False
        }
        return values

    def _get_expense_account_destination(self):
        self.ensure_one()
        account_dest = self.env['account.account']
        if self.payment_mode == 'company_account':
            journal = self.sheet_id.bank_journal_id
            account_dest = (
                journal.outbound_payment_method_line_ids[0].payment_account_id
                or journal.company_id.account_journal_payment_credit_account_id
            )
        elif self.payment_mode == 'petty_cash':
            account_dest = self.supplier_id.property_account_payable_id or self.supplier_id.parent_id.property_account_payable_id
        else:
            if not self.employee_id.sudo().address_home_id:
                raise UserError(_("No Home Address found for the employee %s, please configure one.") % (self.employee_id.name))
            partner = self.employee_id.sudo().address_home_id.with_company(self.company_id)
            account_dest = partner.property_account_payable_id or partner.parent_id.property_account_payable_id
        return account_dest.id

    def _get_account_move_line_values(self):
        if self.supplier_id:
            move_line_values_by_expense = {}
            for expense in self:
                move_line_name = expense.employee_id.name + ': ' + expense.name.split('\n')[0][:64]
                account_src = expense._get_expense_account_source()
                account_dst = expense._get_expense_account_destination()
                account_date = expense.sheet_id.accounting_date or expense.date or fields.Date.context_today(expense)

                company_currency = expense.company_id.currency_id

                move_line_values = []
                unit_amount = expense.unit_amount or expense.total_amount
                quantity = expense.quantity if expense.unit_amount else 1
                taxes = expense.tax_ids.with_context(round=True).compute_all(unit_amount, expense.currency_id,quantity,expense.product_id)
                total_amount = 0.0
                total_amount_currency = 0.0
                partner_id = expense.supplier_id.id

                # source move line
                balance = expense.currency_id._convert(taxes['total_excluded'], company_currency, expense.company_id, account_date)
                amount_currency = taxes['total_excluded']
                move_line_src = {
                    'name': move_line_name,
                    'quantity': expense.quantity or 1,
                    'debit': balance if balance > 0 else 0,
                    'credit': -balance if balance < 0 else 0,
                    'amount_currency': amount_currency,
                    'account_id': account_src.id,
                    'product_id': expense.product_id.id,
                    'product_uom_id': expense.product_uom_id.id,
                    'analytic_account_id': expense.analytic_account_id.id,
                    'analytic_tag_ids': [(6, 0, expense.analytic_tag_ids.ids)],
                    'expense_id': expense.id,
                    'partner_id': partner_id,
                    'tax_ids': [(6, 0, expense.tax_ids.ids)],
                    'tax_tag_ids': [(6, 0, taxes['base_tags'])],
                    'currency_id': expense.currency_id.id,
                }
                move_line_values.append(move_line_src)
                total_amount -= balance
                total_amount_currency -= move_line_src['amount_currency']

                # taxes move lines
                for tax in taxes['taxes']:
                    balance = expense.currency_id._convert(tax['amount'], company_currency, expense.company_id, account_date)
                    amount_currency = tax['amount']

                    if tax['tax_repartition_line_id']:
                        rep_ln = self.env['account.tax.repartition.line'].browse(tax['tax_repartition_line_id'])
                        base_amount = self.env['account.move']._get_base_amount_to_display(tax['base'], rep_ln)
                        base_amount = expense.currency_id._convert(base_amount, company_currency, expense.company_id, account_date)
                    else:
                        base_amount = None

                    move_line_tax_values = {
                        'name': tax['name'],
                        'quantity': 1,
                        'debit': balance if balance > 0 else 0,
                        'credit': -balance if balance < 0 else 0,
                        'amount_currency': amount_currency,
                        'account_id': tax['account_id'] or move_line_src['account_id'],
                        'tax_repartition_line_id': tax['tax_repartition_line_id'],
                        'tax_tag_ids': tax['tag_ids'],
                        'tax_base_amount': base_amount,
                        'expense_id': expense.id,
                        'partner_id': partner_id,
                        'currency_id': expense.currency_id.id,
                        'analytic_account_id': expense.analytic_account_id.id if tax['analytic'] else False,
                        'analytic_tag_ids': [(6, 0, expense.analytic_tag_ids.ids)] if tax['analytic'] else False,
                    }
                    total_amount -= balance
                    total_amount_currency -= move_line_tax_values['amount_currency']
                    move_line_values.append(move_line_tax_values)

                # destination move line
                move_line_dst = {
                    'name': move_line_name,
                    'debit': total_amount > 0 and total_amount,
                    'credit': total_amount < 0 and -total_amount,
                    'account_id': account_dst,
                    'date_maturity': account_date,
                    'amount_currency': total_amount_currency,
                    'currency_id': expense.currency_id.id,
                    'expense_id': expense.id,
                    'partner_id': partner_id,
                    'exclude_from_invoice_tab': True,
                }
                move_line_values.append(move_line_dst)

                move_line_values_by_expense[expense.id] = move_line_values
            return move_line_values_by_expense
        else:
            return super(HrExpense, self)._get_account_move_line_values()


    @api.onchange('employee_id')
    def get_supplier_id(self):
        for move in self:
            proveedor_generico = self.sudo().env['res.partner'].search([('barcode', '=', "GLOBAL")])
            move.supplier_id = proveedor_generico.id if proveedor_generico.id else False

            regla = self.sudo().env['account.analytic.default'].search([('user_id', '=', self.env.user.id)])
            move.analytic_account_id = regla.analytic_id.id
            move.analytic_tag_ids = regla.analytic_tag_ids


    @api.onchange('importe_impuesto')
    def get_impuesto_tag(self):
        for move in self:
            if move.subtotal_gasto:
                tasa = round(((move.importe_impuesto * 100)/move.subtotal_gasto),2)

                move.impuesto_tag = self.sudo().env['account.tax'].search([('price_include', '=', True), ('amount', '=', tasa)])


    def add_to_tax_ids(self):
        for move in self:
            move.write({'tax_ids': [(4, move.impuesto_tag.id)]})
