# -*- coding: utf-8 -*-

from odoo import models, fields


class PortalUserResPartner(models.Model):
    _inherit = 'res.company'

    base_url = fields.Char(string='Base URL', help='For example - http://localhost:8069')
    user_template_id = fields.Many2one('res.users', string='User Template', domain="[('active', '=', False)]")
    portal_mail_id = fields.Many2one('mail.template', string='Portal Email Template', domain="[('model', '=', 'portal.wizard.user')]")
    email_template_id = fields.Many2one('mail.template', string='Password Reset Template', domain="[('model', '=', 'res.users')]")