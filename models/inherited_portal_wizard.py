# -*- coding: utf-8 -*-

import logging

from odoo.tools.translate import _
from odoo import models, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class PortalUserPortalWizardUser(models.TransientModel):
    _inherit = 'portal.wizard.user'

    @api.multi
    def _send_email(self):
        """ send notification email to a new portal user """
        if not self.env.user.email:
            raise UserError(_('You must have an email address in your User Preferences to send emails.'))

        # determine subject and body in the portal user's language
        # template = self.env.ref('portal.mail_template_data_portal_welcome')
        for wizard_line in self:
            lang = wizard_line.user_id.lang
            partner = wizard_line.user_id.partner_id
            template = partner.company_id.portal_mail_id

            portal_url = partner.with_context(signup_force_type_in_url='', lang=lang)._get_signup_url_for_action()[
                partner.id]
            partner.signup_prepare()

            if template:
                template.with_context(dbname=self._cr.dbname, portal_url=portal_url, lang=lang).send_mail(
                    wizard_line.id, force_send=True)
            else:
                _logger.warning("No email template found for sending email to the portal user")

        return True

    @api.multi
    def get_error_messages(self):
        '''
        extending method to check if user has company id set and if all companies have portal email template
        '''

        company_error_template = self.env['res.company']
        partners_error_company = self.env['res.partner']

        res = super(PortalUserPortalWizardUser, self).get_error_messages()

        for wizard_user in self.with_context(active_test=False).filtered(lambda w: w.in_portal and not w.partner_id.user_ids):
            print wizard_user.partner_id.name
            if not wizard_user.partner_id.company_id:
                partners_error_company |= wizard_user.partner_id
        for company in self.with_context(active_test=False).filtered(lambda w: w.in_portal and not w.partner_id.user_ids).mapped('partner_id.company_id'):
            if not company.portal_mail_id:
                company_error_template |= company

        error_msg = []
        if partners_error_company:
            error_msg.append("%s\n- %s" % (_("Some contacts don't have a company set: "),
                                                   '\n- '.join(partners_error_company.mapped('display_name'))))
        if company_error_template:
            error_msg.append("%s\n- %s" % (_("Some companies dont have portal email template set: "),
                                           '\n- '.join(company_error_template.mapped('display_name'))))

        if error_msg:
            res.extend(error_msg)
        return res

