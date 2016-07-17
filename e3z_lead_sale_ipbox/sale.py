# -*- coding: utf-8 -*-
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-2013 Elanz (<http://www.openelanz.fr>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

__author__ = 'vchemiere'

from openerp.osv import osv, fields
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp import netsvc
from openerp import tools
from openerp import SUPERUSER_ID
from openerp.tools.float_utils import float_round
from openerp.addons.sale import sale
from openerp.addons.sale_stock import sale_stock
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import time
import datetime

class sale_order(osv.osv):

    _name = 'sale.order'
    _inherit = ['sale.order', 'mail.thread']

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('sale.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()

    def onchange_partner_id(
            self, cr, uid, ids, partner_id, context=None):
        partner_obj = self.pool['res.partner']
        config_obj = self.pool['ir.config_parameter']
        res = super(sale_order, self).onchange_partner_id(
            cr, uid, ids, partner_id, context=context)
        distribution_costs = float(config_obj.get_param(
            cr, uid, 'distribution_costs'))
        if partner_id:
            partner_costs = partner_obj.browse(
                cr, uid, partner_id, context=context).distribution_costs
            distribution_costs += partner_costs
        res['value']['distribution_costs'] = distribution_costs
        return res


    def _get_margin_percent(self, cr, uid, ids, field_name, arg, context):
        order_obj = self.pool.get('sale.order')
        res = {}
        for order in order_obj.browse(cr, uid, ids):
            cost_total = 0
            cost_total = order.amount_untaxed
            if cost_total != 0:
                res[order.id] = order.margin * 100 / cost_total
            else:
                res[order.id] = 0
        return res

    def _product_margin(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for sale in self.browse(cr, uid, ids, context=context):
            result[sale.id] = 0.0
            for line in sale.order_line:
                result[sale.id] += line.margin or 0.0
        return result

    _columns = {
        'lead_id': fields.many2one('crm.lead', 'Lead'),
        'lead_name': fields.char('Lead name', size=128),
        'lead_stage': fields.related('lead_id', 'stage_id', type="many2one", relation='crm.case.stage', string="Lead stage", store=False),
        'planned_revenue': fields.related('lead_id', 'planned_revenue', type='float', string='Planned Revenue', store=False),
        'probability': fields.related('lead_id', 'probability', type='float', string='Probability', store=False),
        'margin_percent': fields.function(_get_margin_percent, type='float', string='Margin in Percent'),
        'distribution_costs': fields.float('Distribution costs'),
        'order_line': fields.one2many('sale.order.line', 'order_id', 'Order Lines', readonly=False, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}),
        'margin': fields.function(_product_margin, string='Margin', help="It gives profitability by calculating the difference between the Unit Price and the cost price.", store={
                'sale.order': (
                    lambda self, cr, uid, ids, c={}: ids,
                    ['distribution_costs'],
                    15),
                'sale.order.line': (
                        _get_order,
                        ['product_uom_qty', 'purchase_price', 'discount', 'price_unit'],
                        15
                    )
                }),
        'nocreate_lead': fields.boolean('Don\'t create lead'),
        }

    def create(self, cr, uid, vals, context=None):
        lead_obj = self.pool.get('crm.lead')
        order_obj = self.pool.get('sale.order')
        planned_revenue = vals.get('planned_revenue', 0)
        proba = vals.get('probability', 0)
        res = super(sale_order, self).create(cr, uid, vals, context)
        order = order_obj.browse(cr, uid, res, context)
        if order.nocreate_lead:
            lead_vals = {'name': order.lead_name, 'planned_revenue': order.amount_total, 'type': 'opportunity',
                         'partner_id': order.partner_id.id, 'sale_id': order.id, 'planned_revenue': planned_revenue,
                         'probability': proba}
            if vals.get('lead_stage', ''):
                lead_vals['stage_id'] = vals.get('lead_stage')
            if vals.get('planned_revenue', 0):
                lead_vals['planned_revenue'] = planned_revenue
            elif order.amount_total:
                lead_vals['planned_revenue'] = order.amount_total
            lead_id = lead_obj.create(cr, uid, lead_vals)
            order.write({'lead_id': lead_id})

        return res



    def write(self, cr, uid, ids, vals, context=None):
        lead_obj = self.pool.get('crm.lead')
        order_obj = self.pool.get('sale.order')

        if not vals.get('lead_id', False):
            for order in order_obj.browse(cr, uid, ids, context):

                if (vals.get('nocreate_lead', False) or order.nocreate_lead) and not order.lead_id:
                    lead_name =  vals.get('lead_name') or order.lead_name
                    lead_amount_total = vals.get('amount_total') or order.amount_total
                    lead_partner_id = vals.get('partner_id') or order.partner_id.id
                    planned_revenue = vals.get('planned_revenue', 0)  or order.planned_revenue
                    proba = vals.get('probability', 0) or order.probability
                    lead_vals = {'name': lead_name, 'planned_revenue': lead_amount_total, 'type': 'opportunity',
                                 'partner_id': lead_partner_id, 'sale_id': order.id, 'planned_revenue': planned_revenue,
                                 'probability': proba}
                    if vals.get('lead_stage', ''):
                        lead_vals['stage_id'] = vals.get('lead_stage')
                    if vals.get('planned_revenue', 0):
                        lead_vals['planned_revenue'] = planned_revenue
                    elif order.amount_total:
                        lead_vals['planned_revenue'] = order.amount_total
                    lead_id = lead_obj.create(cr, uid, lead_vals)
                    order.write({'lead_id': lead_id, 'lead_name': vals.get('lead_name')})
        return super(sale_order, self).write(cr, uid, ids, vals, context)

    def create_update_lead(self, cr, uid, ids, context=None):
        order_obj = self.pool.get('sale.order')
        lead_obj = self.pool.get('crm.lead')
        for order in order_obj.browse(cr, uid, ids):
            if not order.lead_name:
                raise osv.except_osv(_('Error!'), _('There is no lead name, please set one before create the opportunity!'))
            if not order.lead_id:
                lead_id = lead_obj.create(cr, uid, {'name': order.lead_name, 'planned_revenue': order.amount_total, 'type': 'opportunity', 'partner_id': order.partner_id.id, 'sale_id': order.id})
                order.write({'lead_id': lead_id})
                order_obj.message_post(cr, uid, order.id, body=_('Lead {} created').format(order.lead_name), context=context)
                lead_obj.message_post(cr, uid, lead_id, body=_('Lead created from {}').format(order.name), context=context)
            else:
                lead_obj.write(cr, uid, order.lead_id.id, {'name': order.lead_name, 'planned_revenue': order.amount_total, 'partner_id': order.partner_id.id, 'sale_id': order.id})
        view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'sale', 'view_order_form')
        view_id = view_ref and view_ref[1] or False,
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sales Order',
            'res_model': 'sale.order',
            'res_id': ids[0],
            'view_type': 'form,tree',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'current',
            'nodestroy': True,
        }

    def action_button_confirm(self, cr, uid, ids, context=None):
        split = False
        message = ''
        for order in self.pool.get('sale.order').browse(cr, uid, ids, context):
            context.update({'shop': order.shop_id.id})
            for line in order.order_line:
                context.update({ 'states': ('confirmed','waiting','assigned','done'), 'what': ('in', 'out') })
                if line.product_id.id:
                    stock_virtual = self.pool.get('product.product').get_product_available(cr, uid, [line.product_id.id], context=context)
                    if line.product_uom_qty > stock_virtual[line.product_id.id] and line.type == 'make_to_stock':
                        diff = line.product_uom_qty - stock_virtual[line.product_id.id]
                        if diff > line.product_uom_qty:
                            diff = line.product_uom_qty

                        if (line.product_uom_qty - diff) > 0:
                            new_line_id = self.pool.get('sale.order.line').copy(cr, uid, line.id)
                            self.pool.get('sale.order.line').write(cr, uid, new_line_id, {'product_uom_qty': line.product_uom_qty - diff, 'product_uos_qty': line.product_uom_qty - diff})
                            split = True
                            message += 'La lignes %s de quantite %d a ete divisee en deux lignes:<br/>' % (line.name, line.product_uom_qty)
                            message += '    - %s de quantite %d <br/>' % (line.name, diff)
                            message += '    - %s de quantite %d <br/><br/>' % (line.name, line.product_uom_qty - diff)

                        line.write({'product_uom_qty': diff, 'product_uos_qty': diff, 'type': 'make_to_order'})


        res = super(sale_order, self).action_button_confirm(cr, uid, ids, context)
        users_obj = self.pool.get('res.users')
        for order in self.pool.get('sale.order').browse(cr, uid, ids, context):
            # if order.partner_id.parent_id:
            #     if order.partner_id.parent_id.credit > order.partner_id.parent_id.credit_limit and not users_obj.has_group(cr, uid, 'account.group_account_user') and not users_obj.has_group(cr, uid, 'account.group_account_manager'):
            #         text_error = _('Credit limit allowed is reached.').format(order.partner_id.parent_id.credit, order.partner_id.parent_id.credit_limit)
            #         if order.partner_id.credit_limit < order.partner_id.credit_usual:
            #             text_error += _('\nInsurance credit: {},\nComputed Credit: {},\nUsual credit: {}').format( order.partner_id.parent_id.credit_limit, order.partner_id.parent_id.credit, order.partner_id.parent_id.credit_usual)
            #         raise osv.except_osv(_('Error!'), text_error)
            # else:
            if order.partner_invoice_id.total_credit > order.partner_invoice_id.credit_limit and not users_obj.has_group(cr, uid, 'account.group_account_user') and not users_obj.has_group(cr, uid, 'account.group_account_manager'):
                text_error = _('Credit limit allowed is reached.').format(order.partner_invoice_id.total_credit, order.partner_invoice_id.credit_limit)
                if order.partner_invoice_id.credit_limit < order.partner_invoice_id.credit_usual:
                    text_error += _('\nInsurance credit: {},\nComputed Credit: {},\nUsual credit: {}').format( order.partner_invoice_id.credit_limit, order.partner_invoice_id.total_credit, order.partner_invoice_id.credit_usual)
                raise osv.except_osv(_('Error!'), text_error)
            if order.lead_id:
                self.pool.get('crm.lead').case_mark_won(cr, uid, [order.lead_id.id], context)

            order.write({'date_order': datetime.datetime.now().strftime('%Y-%m-%d')})

            # if split:
            #     res = self.pool.get('warning').info(cr, uid, title='Divisions de lignes', message=message)
        return res

    def action_cancel(self, cr, uid, ids, context=None):
        res = super(sale_order, self).action_cancel(cr, uid, ids, context)
        for order in self.pool.get('sale.order').browse(cr, uid, ids):
            if order.lead_id:
                self.pool.get('crm.lead').case_mark_lost(cr, uid, [order.lead_id.id], context)
        return res

    def message_post(self, cr, uid, thread_id, body='', subject=None, type='notification',
                        subtype=None, parent_id=False, attachments=None, context=None,
                        content_subtype='html', **kwargs):
        res = super(sale_order, self).message_post(cr, uid, thread_id, body, subject, type, subtype, parent_id, attachments, context, content_subtype, **kwargs)

        mail_message = self.pool.get('mail.message')
        ir_attachment = self.pool.get('ir.attachment')

        email_from = kwargs.get('email_from')
        if email_from and thread_id and type == 'email' and kwargs.get('author_id'):
            email_list = tools.email_split(email_from)
            doc = self.browse(cr, uid, thread_id, context=context)
            if email_list and doc:
                author_ids = self.pool.get('res.partner').search(cr, uid, [
                                        ('email', 'ilike', email_list[0]),
                                        ('id', 'in', [f.id for f in doc.message_follower_ids])
                                    ], limit=1, context=context)
                if author_ids:
                    kwargs['author_id'] = author_ids[0]
        author_id = kwargs.get('author_id')
        if author_id is None:  # keep False values
            author_id = self.pool.get('mail.message')._get_default_author(cr, uid, context=context)

        model = False
        if thread_id:
            model = context.get('thread_model', self._name) if self._name == 'mail.thread' else self._name
            if model != self._name:
                del context['thread_model']
                return self.pool.get(model).message_post(cr, uid, thread_id, body=body, subject=subject, type=type, subtype=subtype, parent_id=parent_id, attachments=attachments, context=context, content_subtype=content_subtype, **kwargs)

        partner_ids = set()
        kwargs_partner_ids = kwargs.pop('partner_ids', [])
        for partner_id in kwargs_partner_ids:
            if isinstance(partner_id, (list, tuple)) and partner_id[0] == 4 and len(partner_id) == 2:
                partner_ids.add(partner_id[1])
            if isinstance(partner_id, (list, tuple)) and partner_id[0] == 6 and len(partner_id) == 3:
                partner_ids |= set(partner_id[2])
            elif isinstance(partner_id, (int, long)):
                partner_ids.add(partner_id)
            else:
                pass  # we do not manage anything else
        if parent_id and not model:
            parent_message = mail_message.browse(cr, uid, parent_id, context=context)
            private_followers = set([partner.id for partner in parent_message.partner_ids])
            if parent_message.author_id:
                private_followers.add(parent_message.author_id.id)
            private_followers -= set([author_id])
            partner_ids |= private_followers

        attachment_ids = kwargs.pop('attachment_ids', []) or []  # because we could receive None (some old code sends None)
        if attachment_ids:
            filtered_attachment_ids = ir_attachment.search(cr, SUPERUSER_ID, [
                ('res_model', '=', 'mail.compose.message'),
                ('create_uid', '=', uid),
                ('id', 'in', attachment_ids)], context=context)
            if filtered_attachment_ids:
                ir_attachment.write(cr, SUPERUSER_ID, filtered_attachment_ids, {'res_model': model, 'res_id': thread_id[0]}, context=context)
        attachment_ids = [(4, id) for id in attachment_ids]

        subtype_id = False
        if subtype:
            if '.' not in subtype:
                subtype = 'mail.%s' % subtype
            ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, *subtype.split('.'))
            subtype_id = ref and ref[1] or False

        if model == 'sale.order':
            model = 'crm.lead'
            if isinstance(thread_id, list):
                thread_id = thread_id[0]
            thread_id = self.pool.get('sale.order').browse(cr, uid, thread_id).lead_id.id

        values = kwargs
        values.update({
            'author_id': author_id,
            'model': model,
            'res_id': thread_id or False,
            'body': body,
            'subject': subject or False,
            'type': type,
            'parent_id': parent_id,
            'attachment_ids': attachment_ids,
            'subtype_id': subtype_id,
            'partner_ids': [(4, pid) for pid in partner_ids],
        })

        # Avoid warnings about non-existing fields
        for x in ('from', 'to', 'cc'):
            values.pop(x, None)

        # Create and auto subscribe the author
        if thread_id:
            msg_id = mail_message.create(cr, uid, values, context=context)
        return res

    def _make_invoice(self, cr, uid, order, lines, context=None):
        res = super(sale_order, self)._make_invoice(cr, uid, order, lines, context)
        self.pool.get('account.invoice').write(cr, uid, res, {'distribution_costs': order.distribution_costs})
        return res

    def print_quotation(self, cr, uid, ids, context=None):
        '''
        This function prints the sales order and mark it as sent, so that we can see more easily the next step of the workflow
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time'
        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(uid, 'sale.order', ids[0], 'quotation_sent', cr)
        datas = {
                 'model': 'sale.order',
                 'ids': ids,
                 'form': self.read(cr, uid, ids[0], context=context),
        }
        return {'type': 'ir.actions.report.xml', 'report_name': 'sale.order.layout', 'datas': datas, 'nodestroy': True}


class sale_order_line(osv.Model):

    _inherit = "sale.order.line"

    def _get_margin_percent(self, cr, uid, ids, field_name, arg, context):
        order_line_obj = self.pool.get('sale.order.line')
        res = {}
        for line in order_line_obj.browse(cr, uid, ids):
            res[line.id] = 0
            if line.product_uom_qty:
                if line.price_unit == 0:
                    res[line.id] = round((line.product_uom_qty*(100.0-line.discount)/100.0) -(line.purchase_price*line.product_uom_qty), 2)
                    # res[line.id] = line.margin * 100 / (line.product_uom_qty)
                    res[line.id] -= line.product_uom_qty * (100.0-line.discount)/100 * line.order_id.distribution_costs / 100.0
                    tmp_res = (line.product_uom_qty*((100.0-line.discount)/100.0))
                    res[line.id] = tmp_res != 0 and (res[line.id] * 100 / tmp_res) or 0
                else:
                    # res[line.id] = line.margin * 100 / (line.price_unit * line.product_uom_qty)
                    res[line.id] = round((line.price_unit*line.product_uom_qty*(100.0-line.discount)/100.0) -(line.purchase_price*line.product_uom_qty), 2)
                    res[line.id] -= line.price_unit * line.product_uom_qty * (100.0-line.discount)/100 * line.order_id.distribution_costs / 100.0
                    tmp_res = (line.price_unit * line.product_uom_qty*((100.0-line.discount)/100.0))
                    res[line.id] = tmp_res != 0 and (res[line.id] * 100 / tmp_res) or tmp_res

        return res

    def _get_margin_display(self, cr, uid, ids, field_name, arg, context):
        order_line_obj = self.pool.get('sale.order.line')
        res = {}
        precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
        for line in order_line_obj.browse(cr, uid, ids):
            if line.product_id:
                res[line.id] = str(line.margin or 0) + ' / ' + str(float_round(line.margin_percent, precision) or 0) + '%'
            else:
                res[line.id] = ''
        return res

    def _product_margin(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = 0
            try:
                if line.product_id:
                    if line.product_uom_qty:
                        res[line.id] = round((line.price_unit*line.product_uom_qty*(100.0-line.discount)/100.0) -(line.purchase_price*line.product_uom_qty), 2)
                    res[line.id] -= line.price_unit * line.product_uom_qty * (100.0-line.discount)/100 * line.order_id.distribution_costs / 100.0
            except:
                pass
        return res

    def _get_qty_display(self, cr, uid, ids, field_name, arg, context):
        line_obj = self.pool.get('sale.order.line')
        res = {}
        for line in line_obj.browse(cr, uid, ids):
            if line.product_id:
                # res[line.id] = str(line.product_id.qty_available) + ' / ' + str(line.product_id.qty_available + line.product_id.outgoing_qty)
                context.update({ 'states': ('confirmed','waiting','assigned','done'), 'what': ('in', 'out') })
                context.update({'shop': line.order_id.shop_id.id})
                stock_virtual = self.pool.get('product.product').get_product_available(cr, uid, [line.product_id.id], context=context)
                context.update({ 'states': ('done',), 'what': ('in', 'out') })
                stock_available = self.pool.get('product.product').get_product_available(cr, uid, [line.product_id.id], context=context)
                res[line.id] = str(stock_available[line.product_id.id]) + ' / ' + str(stock_virtual[line.product_id.id])
            else:
                res[line.id] = ''
        return res

    def _get_puvr(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        line_obj = self.pool.get('sale.order.line')
        for line in line_obj.browse(cr, uid, ids):
            res[line.id] = line.price_unit - (line.discount *line.price_unit / 100)

        return res

    def _get_order_line(self, cr, uid, ids, context=None):
        line_ids = []
        for id in ids:
            order = self.pool.get('sale.order').browse(cr, uid, id)
            for line in order.order_line:
                line_ids.append(line.id)
        return line_ids


    _columns = {
        'margin_percent': fields.function(_get_margin_percent, type='float', string='Margin in Percent', digits_compute=dp.get_precision('Account')),
        'margin': fields.function(_product_margin, string='Margin', store={
            'sale.order': (
                _get_order_line,
                ['distribution_costs'],
                10),
            'sale.order.line': (
                lambda self, cr, uid, ids, c={}: ids,
                ['product_uom_qty', 'purchase_price', 'discount', 'price_unit'],
                10
            )
        }),
        'margin_display': fields.function(_get_margin_display, type='char', string='Margin'),
        'product_qty_available': fields.related('product_id', 'qty_available', type='float', string='Qty available'),
        'qty_display': fields.function(_get_qty_display, type='char', string='Qty/Available', context="{'shop_id': order_id.shop_id}"),
        'puvr': fields.function(_get_puvr, string='PUVR', type="float"),
    }

    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        res = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty=qty,
            uom=uom, qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id,
            lang=lang, update_tax=update_tax, date_order=date_order, packaging=packaging, fiscal_position=fiscal_position, flag=flag, context=context)
        if not pricelist:
            return res
        frm_cur = self.pool.get('res.users').browse(cr, uid, uid).company_id.currency_id.id
        to_cur = self.pool.get('product.pricelist').browse(cr, uid, [pricelist])[0].currency_id.id
        if product:
            purchase_price = self.pool.get('product.product').browse(cr, uid, product).purchase_price
            cost_price = self.pool.get('product.product').browse(cr, uid, product).standard_price
            # if purchase_price > cost_price:
            #     pprice = purchase_price
            # elif purchase_price < cost_price:
            #     pprice = cost_price
            # else:
            #     pprice = 0
            pprice = purchase_price
            price = self.pool.get('res.currency').compute(cr, uid, frm_cur, to_cur, pprice, round=False)
            res['value'].update({'purchase_price': price})
            if context.get('from_qty', False):
                if res['value'].get('purchase_price', False) is not False:
                    del(res['value']['purchase_price'])
                if res['value'].get('price_unit', False) is not False:
                    del(res['value']['price_unit'])
        return res

    def button_dummy(self, cr, uid, ids, context=None):
        return True


def product_id_change2(self, cr, uid, ids, pricelist, product, qty=0,
        uom=False, qty_uos=0, uos=False, name='', partner_id=False,
        lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
    context = context or {}
    lang = lang or context.get('lang',False)
    if not  partner_id:
        raise osv.except_osv(_('No Customer Defined!'), _('Before choosing a product,\n select a customer in the sales form.'))
    warning = {}
    product_uom_obj = self.pool.get('product.uom')
    partner_obj = self.pool.get('res.partner')
    product_obj = self.pool.get('product.product')
    context = {'lang': lang, 'partner_id': partner_id}
    if partner_id:
        lang = partner_obj.browse(cr, uid, partner_id).lang
    context_partner = {'lang': lang, 'partner_id': partner_id}

    if not product:
        return {'value': {'th_weight': 0,
            'product_uos_qty': qty}, 'domain': {'product_uom': [],
               'product_uos': []}}
    if not date_order:
        date_order = time.strftime(DEFAULT_SERVER_DATE_FORMAT)

    result = {}
    warning_msgs = ''
    product_obj = product_obj.browse(cr, uid, product, context=context_partner)

    uom2 = False
    if uom:
        uom2 = product_uom_obj.browse(cr, uid, uom)
        if product_obj.uom_id.category_id.id != uom2.category_id.id:
            uom = False
    if uos:
        if product_obj.uos_id:
            uos2 = product_uom_obj.browse(cr, uid, uos)
            if product_obj.uos_id.category_id.id != uos2.category_id.id:
                uos = False
        else:
            uos = False
    fpos = fiscal_position and self.pool.get('account.fiscal.position').browse(cr, uid, fiscal_position) or False
    if update_tax: #The quantity only have changed
        result['tax_id'] = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, product_obj.taxes_id)

    if not flag:
        # result['name'] = self.pool.get('product.product').name_get(cr, uid, [product_obj.id], context=context_partner)[0][1]
        result['name'] = product_obj.name
        if product_obj.description_sale:
            result['name'] += '\n'+product_obj.description_sale
    domain = {}
    if (not uom) and (not uos):
        result['product_uom'] = product_obj.uom_id.id
        if product_obj.uos_id:
            result['product_uos'] = product_obj.uos_id.id
            result['product_uos_qty'] = qty * product_obj.uos_coeff
            uos_category_id = product_obj.uos_id.category_id.id
        else:
            result['product_uos'] = False
            result['product_uos_qty'] = qty
            uos_category_id = False
        result['th_weight'] = qty * product_obj.weight
        domain = {'product_uom':
                    [('category_id', '=', product_obj.uom_id.category_id.id)],
                    'product_uos':
                    [('category_id', '=', uos_category_id)]}
    elif uos and not uom: # only happens if uom is False
        result['product_uom'] = product_obj.uom_id and product_obj.uom_id.id
        result['product_uom_qty'] = qty_uos / product_obj.uos_coeff
        result['th_weight'] = result['product_uom_qty'] * product_obj.weight
    elif uom: # whether uos is set or not
        default_uom = product_obj.uom_id and product_obj.uom_id.id
        q = product_uom_obj._compute_qty(cr, uid, uom, qty, default_uom)
        if product_obj.uos_id:
            result['product_uos'] = product_obj.uos_id.id
            result['product_uos_qty'] = qty * product_obj.uos_coeff
        else:
            result['product_uos'] = False
            result['product_uos_qty'] = qty
        result['th_weight'] = q * product_obj.weight        # Round the quantity up

    if not uom2:
        uom2 = product_obj.uom_id
    # get unit price

    if not pricelist:
        warn_msg = _('You have to select a pricelist or a customer in the sales form !\n'
                'Please set one before choosing a product.')
        warning_msgs += _("No Pricelist ! : ") + warn_msg +"\n\n"
    else:
        price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist],
                product, qty or 1.0, partner_id, {
                    'uom': uom or result.get('product_uom'),
                    'date': date_order,
                    })[pricelist]
        if price is False:
            warn_msg = _("Cannot find a pricelist line matching this product and quantity.\n"
                    "You have to change either the product, the quantity or the pricelist.")

            warning_msgs += _("No valid pricelist line found ! :") + warn_msg +"\n\n"
        else:
            result.update({'price_unit': price})
    if warning_msgs:
        warning = {
                   'title': _('Configuration Error!'),
                   'message' : warning_msgs
                }
    return {'value': result, 'domain': domain, 'warning': warning}

sale.sale_order_line.product_id_change = product_id_change2


def _create_pickings_and_procurements2(self, cr, uid, order, order_lines, picking_id=False, context=None):
    """Create the required procurements to supply sales order lines, also connecting
    the procurements to appropriate stock moves in order to bring the goods to the
    sales order's requested location.

    If ``picking_id`` is provided, the stock moves will be added to it, otherwise
    a standard outgoing picking will be created to wrap the stock moves, as returned
    by :meth:`~._prepare_order_picking`.

    Modules that wish to customize the procurements or partition the stock moves over
    multiple stock pickings may override this method and call ``super()`` with
    different subsets of ``order_lines`` and/or preset ``picking_id`` values.

    :param browse_record order: sales order to which the order lines belong
    :param list(browse_record) order_lines: sales order line records to procure
    :param int picking_id: optional ID of a stock picking to which the created stock moves
                           will be added. A new picking will be created if ommitted.
    :return: True
    """
    move_obj = self.pool.get('stock.move')
    picking_obj = self.pool.get('stock.picking')
    procurement_obj = self.pool.get('procurement.order')
    proc_ids = []

    for line in order_lines:
        if line.state == 'done':
            continue

        date_planned = self._get_date_planned(cr, uid, order, line, order.date_order, context=context)

        if line.product_id:
            if line.product_id.type in ('product', 'consu'):
                if not picking_id:
                    picking_id = picking_obj.create(cr, uid, self._prepare_order_picking(cr, uid, order, context=context))
                move_id = move_obj.create(cr, uid, self._prepare_order_line_move(cr, uid, order, line, picking_id, date_planned, context=context))
            else:
                # a service has no stock move
                move_id = False
            proc_id = procurement_obj.create(cr, uid, self._prepare_order_line_procurement(cr, uid, order, line, move_id, date_planned, context=context))
            proc_ids.append(proc_id)
            line.write({'procurement_id': proc_id})
            self.ship_recreate(cr, uid, order, line, move_id, proc_id)

    wf_service = netsvc.LocalService("workflow")
    if picking_id:
        wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)
    for proc_id in proc_ids:
        wf_service.trg_validate(uid, 'procurement.order', proc_id, 'button_confirm', cr)

    val = {}
    if order.state == 'shipping_except':
        val['state'] = 'progress'
        val['shipped'] = False

        if (order.order_policy == 'manual'):
            for line in order.order_line:
                if (not line.invoiced) and (line.state not in ('cancel', 'draft')):
                    val['state'] = 'manual'
                    break
    order.write(val)
    return True

sale_stock.sale_order._create_pickings_and_procurements = _create_pickings_and_procurements2
