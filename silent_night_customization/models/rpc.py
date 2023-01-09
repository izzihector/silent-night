import odoorpc
import urllib
from odoo import models, _, api, fields
import urllib.request
import re
import xmlrpc.client
from datetime import date, datetime
from xmlrpc.client import dumps, loads

from markupsafe import Markup
from werkzeug.wrappers import Response

from odoo.http import Controller, dispatch_rpc, request, route
from odoo.service import wsgi_server
from odoo.fields import Date, Datetime, Command
from odoo.tools import lazy, ustr
from odoo.tools.misc import frozendict


class Account(models.Model):
    _inherit = 'account.account'

    def rpc(self):
        # Prepare the connection to the server
        # odoo = odoorpc.ODOO('localhost', port=8069)
        pwd_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
        pwd_mgr.add_password(None, "https://erp.silentnight.ae", "admin", "SilentNightOdoo")
        auth_handler = urllib.request.HTTPBasicAuthHandler(pwd_mgr)
        opener = urllib.request.build_opener(auth_handler)
        # odoo = odoorpc.ODOO('example.net', port=80, opener=opener)
        odoo = odoorpc.ODOO('erp.silentnight.ae', protocol='jsonrpc+ssl',opener=opener, port=443)
        # Check available databases
        print(odoo.db.list())
        # Login
        odoo.login(odoo.db.list()[0], 'admin', 'SilentNightOdoo')
        db = odoo.db.list()[0]
        uid = 'admin'
        password = 'SilentNightOdoo'
        # Current user
        user = odoo.env.user
        # Simple 'raw' query
        # user_data = odoo.execute('res.users', 'read', [user.id])

        # SALE ORDER
        jan_2022 = str(datetime.strptime('2022-01-01 00:00:00', '%Y-%m-%d %H:%M:%S'))
        dec_2022 = str(datetime.strptime('2022-12-31 00:00:00', '%Y-%m-%d %H:%M:%S'))
        exiting_so = self.env['sale.order'].search([]).mapped('x_id')
        sale_orders = odoo.env['sale.order'].search(
            [('id', 'not in', exiting_so), ('create_date', '>=', jan_2022), ('create_date', '<=', dec_2022),
             ('state', '=', 'sale')], order='id asc', limit=40)
        counter = 0
        for sl_id in sale_orders:
            if sl_id not in [38520, 38521]:
                so = odoo.env['sale.order'].browse(sl_id)
                # print(so.updated_in_shopify)
                sale_order_id = self.env['sale.order'].create({
                    'x_id': so.id,
                    'name': so.name,
                    'partner_id': self.get_partner_id(so),
                    'makan_number': so.dest_makani_number,
                    'delivery_date': so.pref_date,
                    'beneficiary_delivery_date': so.beneficiary_delivery_date,
                    'analytic_account': self.get_acc_id(so),
                    'beneficiary': self.get_benef_id(so),
                    'client_order_ref': so.client_order_ref,
                    'date_order': so.date_order,
                    'pricelist_id': self.get_pricelist_id(so),
                    'payment_term_id': self.get_payment_term_id(so),
                    'warehouse_id': self.get_warehouse_id(so),
                    'credit_limit': so.credit_limit,
                    'earliest_due_date': so.earliest_due_date,
                    'state': so.state,
                    'updated_in_shopify': so.updated_in_shopify
                })
                counter += 1
                print("==========", counter)

    def get_partner_id(self, aa):
        if aa.partner_id:
            partner = self.env['res.partner'].search([('name', '=', aa.partner_id.name)], limit=1)
            if partner:
                return partner.id
            else:
                x_partner = self.env['res.partner'].create({

                    'name': aa.name
                })
                return x_partner.id
        else:
            return False
        print("CUSTOMER")

    def get_benef_id(self, aa):
        if aa.partner_id:
            partner = self.env['res.partner'].search([('name', '=', aa.partner_id_beneficiary.name)], limit=1)
            if partner:
                return partner.id
            else:
                x_partner = self.env['res.partner'].create({

                    'name': aa.partner_id_beneficiary.name
                })
                return x_partner.id
        else:
            return False
        print("BENEFICIARY")

    def get_warehouse_id(self, so):
        if so.warehouse_id:
            pt = self.env['stock.warehouse'].search([('name', '=', so.warehouse_id.name)], limit=1)
            if pt:
                return pt.id
        else:
            return False
        print("WAREHOUSE")

    def get_payment_term_id(self, so):
        if so.payment_term_id:
            pt = self.env['account.payment.term'].search([('name', '=', so.payment_term_id.name)], limit=1)
            if pt:
                return pt.id
        else:
            return False
        print("PAYMENT TERM")

    def get_pricelist_id(self, so):
        if so.pricelist_id:
            pricelst = self.env['product.pricelist'].search([('x_id', '=', so.pricelist_id.id)])
            if pricelst:
                return pricelst.id
        else:
            return False
        print("PRICELIST")

    def get_acc_id(self, so):
        if so.analytic_account_id:
            acc = self.env['account.analytic.account'].search([('x_id', '=', so.analytic_account_id.id)])
            if acc:
                return acc.id
        else:
            return False
        print("A ACCOUNT")
        # for pid in product_ids:
        #     product_data = odoo.execute('product.template', 'read', [pid])
        # print(user_data)

        # Use all methods of a model
        # if 'sale.order' in odoo.env:
        #     Order = odoo.env['sale.order']
        #     order_ids = Order.search([],limit=1)
        #     for order in Order.browse(order_ids):
        #         print(order.name)
        #         products = [line.product_id.name for line in order.order_line]
        #         print(products)
        #
        # # Update data through a record
        # user.name = "Brian Jones"