# Copyright 2017 theloop Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import binascii
import unittest
import time
import jsonrpcclient
from secp256k1 import PrivateKey

from tests.helper import validator_v2
from tests.helper.wallet import Wallet, ICX_FACTOR


class TestV2(unittest.TestCase):
    process = None  # rest server
    host = 'http://localhost:9000/api/v2'
    first_block = None

    god_private_key = PrivateKey(binascii.unhexlify('98dc1847168d72e515c9e2a6639ae8af312a1dde5d19f3fb38ded71141a1e6be'))
    god_wallet = Wallet(god_private_key)

    any_wallets = [Wallet(), Wallet()]
    any_icx = [123, 1.23]
    tx_hashes = []

    @classmethod
    def setUpClass(cls):
        response = jsonrpcclient.request(cls.host, 'icx_getLastBlock')
        cls.first_block = response

        cls.god_wallet.to_address = cls.any_wallets[0].address
        cls.god_wallet.value = cls.any_icx[0]
        params = cls.god_wallet.create_icx_origin()

        response = jsonrpcclient.request(cls.host, 'icx_sendTransaction', params)
        cls.tx_hashes.append(response)

        time.sleep(1)  # wait for consensus

        cls.any_wallets[0].to_address = cls.any_wallets[1].address
        cls.any_wallets[0].value = cls.any_icx[1]
        params = cls.any_wallets[0].create_icx_origin()

        response = jsonrpcclient.request(cls.host, 'icx_sendTransaction', params)
        cls.tx_hashes.append(response)

        time.sleep(1)  # wait for consensus

    @classmethod
    def tearDownClass(cls):
        pass

    def test_get_transaction_result(self):
        pass

    def test_get_balance(self):
        response = jsonrpcclient.request(self.host, 'icx_getBalance', {"address": self.any_wallets[0].address})
        self.assertEqual(response, hex(int((123 - 1.23) * ICX_FACTOR)))

        response = jsonrpcclient.request(self.host, 'icx_getBalance', {"address": self.any_wallets[1].address})
        self.assertEqual(response, hex(int(1.23 * ICX_FACTOR)))

    def test_get_last_block(self):
        response = jsonrpcclient.request(self.host, 'icx_getLastBlock')
        validator_v2.validate_block(self, response['block'])

        self.assertEqual(response['block']['height'], self.first_block['block']['height'] + len(self.any_icx))

    def test_get_block_by_hash(self):
        response = jsonrpcclient.request(self.host, 'icx_getBlockByHash', {'hash': self.first_block['block']['block_hash']})
        validator_v2.validate_block(self, response['block'])

        self.assertDictEqual(response, self.first_block)

    def test_get_block_by_height(self):
        response = jsonrpcclient.request(self.host, 'icx_getBlockByHeight', {'height': '2'})
        validator_v2.validate_block(self, response['block'])

    def test_get_transaction_by_address(self):
        pass

    def test_get_total_supply(self):
        response = jsonrpcclient.request(self.host, 'icx_getTotalSupply')
        self.assertEqual(response, '0x296f3bc3cac14e365700000')
