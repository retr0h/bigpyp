# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2013, AT&T Services, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations

import datetime
import re

import cert
import utils


class Profile(object):
    """
    A class to manage a local load balancer's profiles.
    """
    def __init__(self, bigip, vips_dict):
        """
        Construct a Profile with the supplied args.

        :param bigip: An instance of the BigIP object.
        :param vips_dict: A dict containing VIP configuration.
        :returns: None
        """
        self._bigip = bigip
        self._vips_dict = vips_dict

    def create(self):
        HTTPProfile(self._bigip).create()
        SSLProfile(self._bigip, self._vips_dict).create()
        TCPProfile(self._bigip).create()


class HTTPProfile(Profile):
    """
    A class to manage a local load balancer's HTTP profile.
    """

    PROFILE_NAME = '/Common/http-xff'
    INSERT_X_FORWARDED_FOR = 'PROFILE_MODE_ENABLED'

    def __init__(self, bigip):
        self._http_profile = bigip.pc.LocalLB.ProfileHttp

    def create(self):
        print 'ProfileHTTP'
        self._create_http_profile()
        self._set_http_profile_x_forward_for()
        self._set_http_profile_default_profile()

    def _create_http_profile(self):
        profiles = self._http_profile.get_list()
        if self.PROFILE_NAME in profiles:
            msg = '  - already exists'
            utils.print_yellow(msg)
        else:
            self._http_profile.create(profile_names=[self.PROFILE_NAME])
            msg = '  - created'
            utils.print_green(msg)

    def _set_http_profile_x_forward_for(self):
        result = self._http_profile \
                     .get_insert_xforwarded_for_header_mode([self.PROFILE_NAME])  # NOQA
        if result[0].value == self.INSERT_X_FORWARDED_FOR:
            msg = '  - already has x-forwarding'
            utils.print_yellow(msg)
        else:
            ctx = self._http_profile.typefactory \
                                    .create('LocalLB.ProfileProfileMode')
            ctx.value = self.INSERT_X_FORWARDED_FOR
            ctx.default_flag = False
            args_dict = {'profile_names': [self.PROFILE_NAME], 'modes': [ctx]}
            self._http_profile \
                .set_insert_xforwarded_for_header_mode(**args_dict)
            msg = '  - added x-forwarding'
            utils.print_green(msg)

    def _set_http_profile_default_profile(self):
        default_profile = '/Common/http'
        result = self._http_profile.get_default_profile([self.PROFILE_NAME])
        #TODO(retr0h): Pycontrol indicates a new http profile's parent
        # is 'http'.  However, `tmsh list /ltm profile http` doesn't seem
        # to agree.
        #
        #  ltm profile http test-pycontrol {
        #      app-service none
        #      insert-xforwarded-for enabled
        #  }
        #
        # Expected:
        #
        #  ltm profile http test-pycontrol {
        #      app-service none
        #      defaults-from http
        #      insert-xforwarded-for enabled
        #  }
        #
        if result[0] == default_profile:
            msg = '  - already has default profile'
            utils.print_yellow(msg)
        else:
            args_dict = {'profile_names': [self.PROFILE_NAME],
                         'defaults': [default_profile]}
            self._http_profile.set_default_profile(**args_dict)
            msg = '  - added default profile'
            utils.print_green(msg)


class SSLProfile(Profile):
    """
    A class to manage a local load balancer's SSL profile.
    """

    def __init__(self, bigip, vips_dict):
        self._ssl_profile = bigip.pc.LocalLB.ProfileClientSSL
        self._vips_dict = vips_dict

    def create(self):
        print 'ProfileClientSSL'
        self._create_ssl_profiles()

    def _create_ssl_profiles(self):
        filtered = utils.filter_on_public(self._vips_dict)
        for vipname, vip_dict in filtered.iteritems():
            domain = vip_dict['dns']
            year = datetime.datetime.now().year
            profile = utils.ssl_profile_name(domain)
            key_profile = '%(year)s-%(domain)s.key' % locals()
            cert_profile = '%(year)s-%(domain)s.crt' % locals()

            self._create_ssl_profile(profile, key_profile, cert_profile)
            self._set_chain_file(profile)

    def _create_ssl_profile(self, profile, key_profile, cert_profile):
        profiles = self._ssl_profile.get_list()

        if profile in profiles:
            msg = '  - {0} already exists'.format(profile)
            utils.print_yellow(msg)
        else:
            struct = 'LocalLB.ProfileString'
            key_ctx = self._ssl_profile.typefactory.create(struct)
            key_ctx.value = key_profile
            key_ctx.default_flag = False

            struct = 'LocalLB.ProfileString'
            cert_ctx = self._ssl_profile.typefactory.create(struct)
            cert_ctx.value = cert_profile
            cert_ctx.default_flag = False

            #TODO(retr0h): Could batch add all at once.
            self._ssl_profile.create_v2(profile_names=[profile],
                                        keys=[key_ctx],
                                        certs=[cert_ctx])
            msg = '  - {0} created'.format(profile)
            utils.print_green(msg)

    def _set_chain_file(self, profile):
        result = self._ssl_profile.get_chain_file([profile])
        cert_basename = '%s.crt' % cert.Cert.INTERMEDIATE_BUNDLE.split('/')[-1]
        re_cert = re.compile(r'%(cert_basename)s' % locals())
        if result[0].value and re_cert.search(result[0].value):
            msg = '  - {0} already has chain file'.format(profile)
            utils.print_yellow(msg)
        else:
            struct = 'LocalLB.ProfileString'
            ctx = self._ssl_profile.typefactory.create(struct)
            ctx.value = '%s.crt' % cert.Cert.INTERMEDIATE_BUNDLE
            ctx.default_flag = False

            self._ssl_profile.set_chain_file(profile_names=[profile],
                                             chains=[ctx])
            msg = '  - {0} added chain file'.format(profile)
            utils.print_green(msg)


class TCPProfile(Profile):
    """
    A class to manage a local load balancer's TCP profile.
    """

    PROFILE_NAME = '/Common/tcp-custom-keepalive'
    KEEP_ALIVE_INTERVAL = 180

    def __init__(self, bigip):
        self._tcp_profile = bigip.pc.LocalLB.ProfileTCP

    def create(self):
        print 'ProfileTCP'
        self._create_tcp_profile()
        self._set_tcp_custom_keepalive()

    def _create_tcp_profile(self):
        profiles = self._tcp_profile.get_list()
        if self.PROFILE_NAME in profiles:
            msg = '  - already exists'
            utils.print_yellow(msg)
        else:
            self._tcp_profile.create(profile_names=[self.PROFILE_NAME])
            msg = '  - created'
            utils.print_green(msg)

    def _set_tcp_custom_keepalive(self):
        result = self._tcp_profile.get_keep_alive_interval([self.PROFILE_NAME])
        if result[0].value == self.KEEP_ALIVE_INTERVAL:
            msg = '  - already has custom keepalive'
            utils.print_yellow(msg)
        else:
            ctx = self._tcp_profile.typefactory.create('LocalLB.ProfileULong')
            ctx.value = self.KEEP_ALIVE_INTERVAL
            ctx.default_flag = False
            args_dict = {'profile_names': [self.PROFILE_NAME],
                         'intervals': [ctx]}
            self._tcp_profile.set_keep_alive_interval(**args_dict)
            msg = '  - added custom keepalive'
            utils.print_green(msg)
