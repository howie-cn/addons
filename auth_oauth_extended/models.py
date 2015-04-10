# -*- coding: utf-8 -*-

import logging

import simplejson
import openerp
from openerp.osv import osv

from openerp.addons.auth_signup.res_users import SignupError

_logger = logging.getLogger(__name__)
from openerp import models, fields


class auth_oauth_provider(models.Model):
    _inherit = 'auth.oauth.provider'

    provider_type = [
        ('qq', 'for QQ'),
        ('weixin', 'for Weixin'),
        ('weibo', 'for Weibo'),
        ('other', 'for Other'),

    ]

    provider_type = fields.Selection(provider_type, 'Provider Type', required=True)


class res_users(osv.Model):
    _inherit = 'res.users'


    def _auth_oauth_signin(self, cr, uid, provider, validation, params, context=None):

        """ retrieve and sign in the user corresponding to provider and validated access token
            :param provider: oauth provider id (int)
            :param validation: result of validation of access token (dict)
            :param params: oauth parameters (dict)
            :return: user login (str)
            :raise: openerp.exceptions.AccessDenied if signin failed

            This method can be overridden to add alternative signin methods.
        """
        try:
            if provider.provider_type == 'qq':
                oauth_uid = validation['openid']
            elif provider.provider_type == 'weixin':
                oauth_uid = validation['openid']
            elif provider.provider_type == 'weibo':
                oauth_uid = validation['userid']
            else:
                oauth_uid = validation['user_id']
            user_ids = self.search(cr, uid, [("oauth_uid", "=", oauth_uid), ('oauth_provider_id', '=', provider)])
            if not user_ids:
                raise openerp.exceptions.AccessDenied()
            assert len(user_ids) == 1
            user = self.browse(cr, uid, user_ids[0], context=context)
            user.write({'oauth_access_token': params['access_token']})
            return user.login
        except openerp.exceptions.AccessDenied, access_denied_exception:
            if context and context.get('no_user_creation'):
                return None
            state = simplejson.loads(params['state'])
            token = state.get('t')
            if provider.provider_type == 'qq':
                oauth_uid = validation['openid']
            elif provider.provider_type == 'weixin':
                oauth_uid = validation['openid']
            elif provider.provider_type == 'weibo':
                oauth_uid = validation['userid']
            else:
                oauth_uid = validation['user_id']
            email = validation.get('email', 'provider_%s_user_%s' % (provider, oauth_uid))
            name = validation.get('name', email)
            values = {
                'name': name,
                'login': email,
                'email': email,
                'oauth_provider_id': provider,
                'oauth_uid': oauth_uid,
                'oauth_access_token': params['access_token'],
                'active': True,
            }
            try:
                _, login, _ = self.signup(cr, uid, values, token, context=context)
                return login
            except SignupError:
                raise access_denied_exception


    def auth_oauth(self, cr, uid, provider, params, context=None):
        # Advice by Google (to avoid Confused Deputy Problem)
        # if validation.audience != OUR_CLIENT_ID:
        # abort()
        # else:
        # continue with the process
        access_token = params.get('access_token')
        validation = super(res_users, self)._auth_oauth_validate(cr, uid, provider, access_token)
        # required check
        if provider.provider_type == 'qq':
            oauth_uid = validation['openid']
        elif provider.provider_type == 'weixin':
            oauth_uid = validation['openid']
        elif provider.provider_type == 'weibo':
            oauth_uid = validation['userid']
        else:
            oauth_uid = 'user_id'

        if not validation.get(oauth_uid):
            raise openerp.exceptions.AccessDenied()
        # retrieve and sign in user
        login = self._auth_oauth_signin(cr, uid, provider, validation, params, context=context)
        if not login:
            raise openerp.exceptions.AccessDenied()
        # return user credentials
        return (cr.dbname, login, access_token)


