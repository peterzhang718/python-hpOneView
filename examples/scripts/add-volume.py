#!/usr/bin/env python3
###
# (C) Copyright 2015 Hewlett-Packard Development Company, L.P.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
###
import sys
if sys.version_info < (3, 4):
    raise Exception('Must use Python 3.4 or later')

import hpOneView as hpov
from pprint import pprint


def acceptEULA(con):
    # See if we need to accept the EULA before we try to log in
    con.get_eula_status()
    try:
        if con.get_eula_status() is True:
            print('EULA display needed')
            con.set_eula('no')
    except Exception as e:
        print('EXCEPTION:')
        print(e)


def login(con, credential):
    # Login with givin credentials
    try:
        con.login(credential)
    except:
        print('Login failed')


def add_volume(sto, name, pool_name, size, shareable=False,
               description='Example Volume', provisionType='Thin'):
    pools = sto.get_storage_pools()
    for pool in pools['members']:
        if pool['name'] == pool_name:
            storagePoolUri = pool['uri']
            print('Adding Volume: ', name)
            volume = hpov.common.make_storage_volume(name,
                                             int(size)*1024*1024*1024,
                                             shareable,
                                             storagePoolUri,
                                             description, provisionType)
            ret = sto.add_storage_volume(volume)
            if 'deviceVolumeName' in ret:
                print('Name:                ', ret['name'])
                print('Type:                ', ret['type'])
                print('State:               ', ret['state'])
                print('Description:         ', ret['description'])
                print('Volume Name:         ', ret['deviceVolumeName'])
                print('Allocated Capacity : ', ret['allocatedCapacity'])
                print('Provisioned Capacity:', ret['provisionedCapacity'])
            else:
                pprint(ret)
            return
    print('Pool: ', pool_name, ' not found')


def main():
    parser = argparse.ArgumentParser(add_help=True, description='Usage',
                        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-a', dest='host', required=True,
                        help='''
    HP OneView Appliance hostname or IP address''')
    parser.add_argument('-u', dest='user', required=False,
                        default='Administrator',
                        help='''
    HP OneView Username''')
    parser.add_argument('-p', dest='passwd', required=True,
                        help='''
    HP OneView Password''')
    parser.add_argument('-c', dest='cert', required=False,
                        help='''
    Trusted SSL Certificate Bundle in PEM (Base64 Encoded DER) Format''')
    parser.add_argument('-y', dest='proxy', required=False,
                        help='''
    Proxy (host:port format''')
    parser.add_argument('-n', dest='name',
                        required=True,
                        help='''
    Name of the storage volume to add''')
    parser.add_argument('-sp', dest='sto_pool',
                        required=True,
                        help='''
    Name of the storage pool to use''')
    parser.add_argument('-cap', '--capacity', dest='size',
                        required=True,
                        help='''
    Size of volume in GiB''')
    parser.add_argument('-sh', '--shareable', dest='shareable',
                        required=False,
                        default=False,
                        action='store_true',
                        help='''
    sets volume to shareable, omit for private''')
    parser.add_argument('-pt', '--prov_type', dest='provType',
                        required=False,
                        default='Thin',
                        help='''
    Thin or Full provisioning''')
    parser.add_argument('-des', '--description', dest='desc',
                        required=False,
                        default='Example Volume',
                        help='''
    Description of volume''')

    args = parser.parse_args()
    credential = {'userName': args.user, 'password': args.passwd}

    con = hpov.connection(args.host)
    sto = hpov.storage(con)

    if args.proxy:
        con.set_proxy(args.proxy.split(':')[0], args.proxy.split(':')[1])
    if args.cert:
        con.set_trusted_ssl_bundle(args.cert)

    login(con, credential)
    acceptEULA(con)

    add_volume(sto, args.name, args.sto_pool, args.size, args.shareable,
               args.desc, args.provType)

if __name__ == '__main__':
    import sys
    import argparse
    sys.exit(main())

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
