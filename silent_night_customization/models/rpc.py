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
        odoo = odoorpc.ODOO('erp.silentnight.ae', protocol='jsonrpc+ssl', opener=opener, port=443)
        # Check available databases
        #print(odoo.db.list())
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
        jan_2022 = str(datetime.strptime('2023-01-01 00:00:00', '%Y-%m-%d %H:%M:%S'))
        dec_2022 = str(datetime.strptime('2023-12-31 00:00:00', '%Y-%m-%d %H:%M:%S'))
        exiting_so = self.env['sale.order'].search([]).mapped('x_id')
        sale_orders = odoo.env['sale.order'].search(
            [('id', 'not in', exiting_so), ('create_date', '>=', jan_2022), ('create_date', '<=', dec_2022),
             ('state', '=', 'sale')], order='id asc', limit=100)
        counter = 0
        for sl_id in sale_orders:
            # if sl_id not in [38520, 38521]:
            so = odoo.execute('sale.order', 'read', [sl_id],
                              ['id', 'name', 'partner_id', 'dest_makani_number', 'pref_date',
                               'beneficiary_delivery_date', 'analytic_account_id', 'partner_id', 'client_order_ref',
                               'date_order', 'pricelist_id', 'payment_term_id', 'warehouse_id', 'credit_limit',
                               'earliest_due_date', 'state'])
            # so = odoo.env['sale.order'].browse(sl_id)
            # print(so.updated_in_shopify)
            sale_order_id = self.env['sale.order'].create({
                'x_id': so[0]['id'],
                'name': so[0]['name'],
                'partner_id': self.get_partner_id(so[0]),
                'makan_number': so[0]['dest_makani_number'],
                'delivery_date': so[0]['pref_date'],
                'beneficiary_delivery_date': so[0]['beneficiary_delivery_date'],
                'analytic_account': self.get_acc_id(so[0]),
                'beneficiary': self.get_benef_id(so[0]),
                'client_order_ref': so[0]['client_order_ref'],
                'date_order': so[0]['date_order'],
                'pricelist_id': self.get_pricelist_id(so[0]),
                'payment_term_id': self.get_payment_term_id(so[0]),
                'warehouse_id': self.get_warehouse_id(so[0]),
                'credit_limit': so[0]['credit_limit'],
                'earliest_due_date': so[0]['earliest_due_date'],
                'state': so[0]['state'],
            })
            counter += 1
            print("==========", counter)

    def get_partner_id(self, aa):
        if aa['partner_id']:
            if "," in aa['partner_id'][1]:
                name = aa['partner_id'][1].split(',')[1].strip()
            else:
                name = aa['partner_id'][1].strip()
            partner = self.env['res.partner'].search([('name', '=', name)],
                                                     limit=1)
            if partner:
                return partner.id
            else:
                x_partner = self.env['res.partner'].create({

                    'name': name
                })
                return x_partner.id
        else:
            return False

    def get_benef_id(self, aa):
        if aa['partner_id']:
            if "," in aa['partner_id'][1]:
                name = aa['partner_id'][1].split(',')[1].strip()
            else:
                name = aa['partner_id'][1].strip()
            partner = self.env['res.partner'].search([('name', '=', name)], limit=1)
            if partner:
                return partner.id
            else:
                x_partner = self.env['res.partner'].create({

                    'name': name
                })
                return x_partner.id
        else:
            return False

    def get_warehouse_id(self, so):
        if so['warehouse_id']:
            pt = self.env['stock.warehouse'].search([('name', '=', so['warehouse_id'][1])], limit=1)
            if pt:
                return pt.id
        else:
            return False

    def get_payment_term_id(self, so):
        if so['payment_term_id']:
            pt = self.env['account.payment.term'].search([('name', '=', so['payment_term_id'][1])], limit=1)
            if pt:
                return pt.id
        else:
            return False

    def get_pricelist_id(self, so):
        if so['pricelist_id']:
            pricelst = self.env['product.pricelist'].search([('x_id', '=', so['pricelist_id'][0])])
            if pricelst:
                return pricelst.id
            else:
                return 19

    def get_acc_id(self, so):
        if so['analytic_account_id']:
            acc = self.env['account.analytic.account'].search([('x_id', '=', so['analytic_account_id'][0])])
            if acc:
                return acc.id
        else:
            return False
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

    def rpc_sale_line(self):
        pwd_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
        pwd_mgr.add_password(None, "https://erp.silentnight.ae", "admin", "SilentNightOdoo")
        auth_handler = urllib.request.HTTPBasicAuthHandler(pwd_mgr)
        opener = urllib.request.build_opener(auth_handler)
        # odoo = odoorpc.ODOO('example.net', port=80, opener=opener)
        odoo = odoorpc.ODOO('erp.silentnight.ae', protocol='jsonrpc+ssl', opener=opener, port=443)
        # Check available databases
        print(odoo.db.list())
        # Login
        odoo.login(odoo.db.list()[0], 'admin', 'SilentNightOdoo')
        db = odoo.db.list()[0]
        uid = 'admin'
        password = 'SilentNightOdoo'
        # Current user
        user = odoo.env.user

        sale_orders = self.env['sale.order'].search([('x_is_updated', '=', False)],limit=100)

        for order_id in sale_orders:
            x_sale_line = odoo.env['sale.order.line'].search([('id', '=', int(order_id.x_id))])
            for x_line_id in x_sale_line:
                x_line = odoo.execute('sale.order.line', 'read', [x_line_id],
                                      ['name', 'product_id', 'product_uom_qty', 'qty_delivered', 'qty_invoiced',
                                       'product_uom', 'price_unit', 'order_id', 'tax_id', 'x_pid'])
                # x_line = odoo.env['sale.order.line'].browse(x_line_id)
                print("X-SO-ID=====>>>>>>>", order_id.x_id)
                if x_line[0]['product_id']:
                    sale_order_line = self.env['sale.order.line'].create({

                        'name': x_line[0]['name'],
                        'product_id': self.get_product_id(x_line[0], odoo),
                        'product_uom_qty': x_line[0]['product_uom_qty'],
                        'qty_delivered': x_line[0]['qty_delivered'],
                        'qty_invoiced': x_line[0]['qty_invoiced'],
                        'product_uom': self.get_product_uom_id(x_line[0]),
                        'price_unit': x_line[0]['price_unit'],
                        'order_id': order_id.id,
                        'tax_id': self.get_tax_id(x_line[0], odoo),
                    })
                order_id.x_is_updated = True
                order_id.x_ref = x_line[0]['order_id'][1]

    def get_tax_id(self, x_line, odoo):
        list = []
        for tax_id in x_line['tax_id']:
            x_tax = odoo.execute('account.tax', 'read', [tax_id], ['name'])
            tax = self.env['account.tax'].search([('name', '=', x_tax[0]['name'])])
            if tax:
                list.append(tax.ids)
        return list

    def get_product_uom_id(self, x_line):
        uom = self.env['uom.uom'].search([('name', '=', x_line['product_uom'][1])])
        if uom:
            return uom.id
        else:
            return False

    def get_product_id(self, x_line, odoo):
        if x_line['product_id']:
            x_product = odoo.execute('product.product', 'read', [x_line['x_pid']],
                                     ['name', 'list_price', 'standard_price'])
            product = self.env['product.product'].search([('name', '=', x_product[0]['name'])], limit=1)
            if product:
                product.update({'x_id': x_product[0]['id']})
                return product.id
            else:
                x_product = self.env['product.product'].create({'x_id': x_product[0]['id'],
                                                                'name': x_product[0]['name'] or "test",
                                                                'sale_ok': True,
                                                                'categ_id': 530,
                                                                'list_price': x_product[0]['list_price'],
                                                                'standard_price': x_product[0]['standard_price']
                                                                })
                return x_product.id
