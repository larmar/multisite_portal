# -*- coding: utf-8 -*-

import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.addons.auth_signup.models.res_partner import SignupError, now
from odoo.tools.misc import ustr
from ast import literal_eval

_logger = logging.getLogger(__name__)


class PortalUserResUsers(models.Model):
    _inherit = 'res.users'

    @api.multi
    def action_reset_password(self):
        '''
        Overridden method to change password reset template to the one
        which is set in the company general information view.
        New user registration template is not changed.
        '''
        if self.company_id.email_template_id:
            create_mode = bool(self.env.context.get('create_user'))
            print 'create mode', create_mode
            # no time limit for initial invitation, only for reset password
            expiration = False if create_mode else now(days=+1)

            self.mapped('partner_id').signup_prepare(signup_type="reset", expiration=expiration)

            # send email to users with their signup url
            template = False
            if create_mode:
                try:
                    #Using standard set_password_mail template
                    template = self.env.ref('auth_signup.set_password_email', raise_if_not_found=False)
                except ValueError:
                    pass
            if not template:
                #password reset from user comapny settings
                template = self.company_id.email_template_id
            assert template._name == 'mail.template'

            for user in self:
                if not user.email:
                    raise UserError(_("Cannot send email: user %s has no email address.") % user.name)
                template.with_context(lang=user.lang).send_mail(user.id, force_send=True, raise_exception=True)
                _logger.info("Password reset email sent for user <%s> to <%s>", user.login, user.email)
        else:
            raise UserError(_('There is no password reset template set for this company, please set it in company settings'))

    @api.model
    def _signup_create_user(self, values):
        '''
        Standard method overridden to take User Template from template set in company parameters
        '''
        IrConfigParam = self.env['ir.config_parameter']

        website_id = self.env.context.get('website_id')
        website_obj = self.env['website'].search([('id', '=', website_id)])
        if website_obj:
            company_id = self.env['res.company'].search([('id', '=', website_obj.company_id.id)])
            if company_id.user_template_id:
                template_user_id = company_id.user_template_id.id
                template_user = self.browse(template_user_id)
                assert template_user.exists(), 'Signup: invalid template user'

                # check that uninvited users may sign up
                if 'partner_id' not in values:
                    if not literal_eval(IrConfigParam.get_param('auth_signup.allow_uninvited', 'False')):
                        raise SignupError('Signup is not allowed for uninvited users')

                assert values.get('login'), "Signup: no login given for new user"
                assert values.get('partner_id') or values.get('name'), "Signup: no name or partner given for new user"

                # create a copy of the template user (attached to a specific partner_id if given)
                values['active'] = True
                try:
                    with self.env.cr.savepoint():
                        res = template_user.with_context(no_reset_password=True).copy(values)
                        return res
                except Exception, e:
                    # copy may failed if asked login is not available.
                    raise SignupError(ustr(e))
            else:
                _logger.info("user template not set for the company")
                raise SignupError('User Template not set for this company, please contact system administrator')
        else:
            _logger.info("website obj not found")
            raise SignupError('Error, please contact system administrator')




