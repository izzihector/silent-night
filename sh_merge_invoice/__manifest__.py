# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Merge Invoices",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "category": "Accounting",
    "license": "OPL-1",
    "summary": """
Merge Invoice App,
Combine Credit Note Module,
Append Debit Note Application,
Merge Vendor Bills,
Merge invoices, merge bills,
merge accounting Odoo
""",
    "description": """
If you want to merge two different invoices/credit note/debit note/
vendor bills? You can easily merge two different invoices/credit note/
debit note/vendor bills using this module.
You can merge only draft stage invoices.
In Merge Invoice wizard,
Select customer and if you want to create new invoice
then don't select invoice.
if you want to merge in existing invoice then select invoice,
choose merge type cancel, remove or do nothing options.
In this module there are 3 different merge types like
1) Do Nothing : No change in other invoices after invoices are merge.
2) Cancel Other Invoices : Cancel other invoices after invoices are merge.
3) Remove Other Invoice : Delete other invoices after invoices are merge.
Merge Invoices Odoo
Combine Invoice Module, Feature Of Append Credit Note,
Mix Debit Note, Merge Vendor Bills Odoo, Merge Invoice Odoo.
Merge Invoice App, Combine Credit Note Module,
Append Debit Note Application, Merge Vendor Bills Odoo.
""",
    "version": "15.0.4",
    "depends": [
        "account",
    ],
    "application": True,
    "data": [
        "security/ir.model.access.csv",
        "wizard/merge_invoice.xml",
    ],
    "images": ["static/description/background.png", ],
    "live_test_url": "https://youtu.be/HTmdR6ohBbM",
    "auto_install": False,
    "installable": True,
    "price": 30,
    "currency": "EUR"
}
