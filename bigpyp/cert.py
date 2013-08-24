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
import os
import re

import utils


class Cert(object):
    """
    A class to manage keys, certificates, and certificate requests.
    """

    MANAGEMENT_MODE_TYPE = 'MANAGEMENT_MODE_DEFAULT'
    FILE_BASEDIR = os.path.join(os.path.dirname(__file__),
                                '..', '..', 'deployment-data',
                                'data_bags', 'certs')
    INTERMEDIATE_BUNDLE = '/Common/verisign_intermediate_bundle'
    RE_ZONE = re.compile(r'\.([a-z]{3}[0-9]).*\.com')

    def __init__(self, bigip, vips_dict):
        """
        Construct Cert with the supplied args.

        :param bigip: An instance of the BigIP object.
        :param vips_dict: A dict containing VIP configuration.
        :returns: None
        """
        self._key_cert = bigip.pc.Management.KeyCertificate
        self._vips_dict = vips_dict

    def create(self):
        print 'Cert'
        self._upload_certs()
        self._upload_intermediate_cert()

    def _upload_certs(self):
        filtered = utils.filter_on_public(self._vips_dict)
        for vipname, vip_dict in filtered.iteritems():
            domain = vip_dict['dns']
            zone_name = self._zone_name(domain)
            year = datetime.datetime.now().year
            name = '/Common/%(year)s-%(domain)s' % locals()
            if zone_name:
                key_file = os.path.join(self.FILE_BASEDIR,
                                        zone_name,
                                        domain,
                                        '%(domain)s.pem' % locals())
                cert_file = os.path.join(self.FILE_BASEDIR,
                                         zone_name,
                                         domain,
                                         '%(domain)s.crt' % locals())
                self._import_key_from_file(name, key_file)
                self._import_certificate_from_file(name, cert_file)

    def _upload_intermediate_cert(self):
        cert_name = self.INTERMEDIATE_BUNDLE
        cert_basename = '%s.crt' % self.INTERMEDIATE_BUNDLE.split('/')[-1]
        cert_file = os.path.join(self.FILE_BASEDIR, cert_basename)
        self._import_certificate_from_file(cert_name, cert_file)

    def _delete(self, name):
        self._key_cert.key_delete(mode=self.MANAGEMENT_MODE_TYPE,
                                  key_ids=[name])
        self._key_cert.certificate_delete(mode=self.MANAGEMENT_MODE_TYPE,
                                          cert_ids=[name])

    def _import_key_from_file(self, key_name, key_file):
        if self._get_key(key_name):
            msg = '  - key {0} already exists'.format(key_name)
            utils.print_yellow(msg)
        else:
            with open(key_file, 'r') as file:
                data = file.read()
                args_dict = {'mode': self.MANAGEMENT_MODE_TYPE,
                             'key_ids': [key_name],
                             'pem_data': [data],
                             'overwrite': False}
                self._key_cert.key_import_from_pem(**args_dict)
                msg = '  - added key {0}'.format(key_name)
                utils.print_green(msg)

    def _import_certificate_from_file(self, cert_name, cert_file):
        if self._get_certificate(cert_name):
            msg = '  - cert {0} already exists'.format(cert_name)
            utils.print_yellow(msg)
        else:
            with open(cert_file, 'r') as file:
                data = file.read()
                args_dict = {'mode': self.MANAGEMENT_MODE_TYPE,
                             'cert_ids': [cert_name],
                             'pem_data': [data],
                             'overwrite': False}
                self._key_cert.certificate_import_from_pem(**args_dict)
                msg = '  - added cert {0}'.format(cert_name)
                utils.print_green(msg)

    def _get_certificate(self, cert):
        args_dict = {'mode': self.MANAGEMENT_MODE_TYPE}
        cert_list = self._key_cert.get_certificate_list(**args_dict)
        for c in cert_list:
            if c.certificate.cert_info['id'] == cert:
                return True
            else:
                pass
        return False

    def _get_key(self, key):
        args_dict = {'mode': self.MANAGEMENT_MODE_TYPE}
        key_list = self._key_cert.get_key_list(**args_dict)
        for k in key_list:
            if k.key_info['id'] == key:
                return True
            else:
                pass
        return False

    def _zone_name(self, domain):
        match = self.RE_ZONE.search(domain)
        if match:
            return match.group(1)
        else:
            return False
