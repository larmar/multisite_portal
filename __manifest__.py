# -*- coding: utf-8 -*-
{
    'name': "multisite_portal",

    'summary': """
        Modification allowing to set custom base URL, portal user creation , email, and password reset template per company.
        """,

    'description': """
        Modification allowing to set custom base URL, portal user creation , email, and password reset template per company.
    """,

    'author': "UAB Pralo",
    'website': "http://www.pralo.eu",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'auth_signup', 'portal'],

    # always loaded
    'data': [
        'views/inherited_res_company.xml',
    ],
}