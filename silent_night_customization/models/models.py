# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


# class silent_night_customization(models.Model):
#     _name = 'silent_night_customization.silent_night_customization'
#     _description = 'silent_night_customization.silent_night_customization'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
class ResPartner(models.Model):
    _inherit = 'res.partner'

    credit_block = fields.Selection([('none','None'),('blocked','Blocked'),('value','Value'),('date','Date'),
                    ('all','All')],default='none')
    credit_limit = fields.Float('Credit Limit')
    credit_limit_days = fields.Integer('Credit Limit Days')
    worst_due_date = fields.Date('Worst Due Date')
    total_rece = fields.Integer('Total Payable')
    total_pay = fields.Integer('Total Receivable')
    # benef = fields.Many2one('res.partner','Beneficiary')

    # def create_invoices(self):
    #     res = super(AccountMove, self).create_invoices()
    #     print()


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    makan_number = fields.Char("Makani Delivery")
    delivery_date = fields.Date("Delivery Date")
    time_slot = fields.Many2one('delivery.time.slot', "Delivery Time Slot")
    beneficiary = fields.Many2one('res.partner', "Beneficiary")
    beneficiary_delivery_date = fields.Date("Benef. Delivery Date")
    analytic_account = fields.Many2one('account.analytic.account', "Analytic Account")
    client_order_Ref = fields.Char("PO Ref.")
    x_origin = fields.Char("Project Name")
    warehouse = fields.Many2one('stock.warehouse', "Warehouse")
    credit_limit = fields.Float("Credit Limit")
    earliest_due_date = fields.Date("Worst Due Date")


class AccountMove(models.Model):
    _inherit = 'account.move'

    subscription_count = fields.Integer('Subscription')
    prepayment_frequency = fields.Selection([('no','No'),('daily','Daily'),('weekly','Weekly'),('monthly','Monthly'),
                                             ('yearly','Yearly')],default='no',string='Amortisation Frequency')

    prepayment_amount = fields.Float('Prepayment Amount')
    prepayment_start_date = fields.Date('Start Date')
    prepayment_account_id = fields.Many2one('account.account',string='Expense Account')
    prepayment_balance = fields.Float('Prepayment Balance')
    prepayment_move_ids = fields.One2many('account.move','prepayment_invoice_id')
    prepayment_invoice_id = fields.Many2one('account.move')

    def scheduler_amortise_prepayment(self):
        print()

    def action_view_subscription(self):
        print()
    @api.model_create_multi
    def create(self, vals_list):
        res = super(AccountMove, self).create(vals_list)
        ctx = self.env.context
        if ctx.get('active_model') == 'sale.order':
            so = self.env['sale.order'].browse(ctx.get('active_id'))
            res.x_beneficiary = so.beneficiary
        return res

    def set_db_date(self):
        params = self.env['ir.config_parameter'].search([('key','=','database.expiration_date')])
        params.update({'value': '2023-12-12 00:00:00'})

class DeliveryTimeSLot(models.Model):
    _name = 'delivery.time.slot'

    name = fields.Char('Time Slot')
    hour = fields.Float('Hour of the day')
    days = fields.Many2one('calendar.day', "Days")


class CalendarDay(models.Model):
    _name = 'calendar.day'

    name = fields.Char('Days')

class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    branch = fields.Char('Branch')
    iban = fields.Char('iban')
