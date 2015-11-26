"""
Copyright 2015 Hewlett-Packard

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""

import os
import unittest
import json
from mock import Mock, patch

import requests

from freezer_api.cmd.db_init import (ElastichsearchEngine,
                                     get_args,
                                     find_config_file,
                                     parse_config_file,
                                     get_db_params,
                                     main,
                                     DEFAULT_CONF_PATH,
                                     MergeMappingException,
                                     NumberOfReplicasException)

from freezer_api.common import db_mappings

class TestElasticsearchEngine(unittest.TestCase):

    def setUp(self):
        self.test_mappings = {
            'jobs': {"properties": {"job_id": {"type": "string"}}},
            'backups': {"properties": {"backup_id": {"type": "string"}}},
            'clients': {"properties": {"client_id": {"type": "string"}}},
        }

        self.mock_resp = Mock()
        self.mock_args = Mock()
        self.mock_args.test_only = False
        self.mock_args.always_yes = False
        self.mock_args.verbose = 1
        self.mock_args.select_mapping = ''
        self.mock_args.erase = False
        self.mock_args.replicas = 0
        self.es_manager = ElastichsearchEngine(es_url='http://test:9333',
                                               es_index='freezerindex',
                                               args=self.mock_args)

    def test_new(self):
        self.assertIsInstance(self.es_manager, ElastichsearchEngine)

    @patch.object(ElastichsearchEngine, 'check_index_exists')
    @patch.object(ElastichsearchEngine, 'mapping_match')
    @patch.object(ElastichsearchEngine, 'askput_mapping')
    @patch.object(ElastichsearchEngine, 'set_number_of_replicas')
    def test_put_mappings_does_nothing_when_mappings_match(self,
                                                           mock_set_number_of_replicas,
                                                           mock_askput_mapping,
                                                           mock_mapping_match,
                                                           mock_check_index_exists):
        self.es_manager.put_mappings(self.test_mappings)
        self.assertEquals(mock_askput_mapping.call_count, 0)

    @patch.object(ElastichsearchEngine, 'check_index_exists')
    @patch.object(ElastichsearchEngine, 'mapping_match')
    @patch.object(ElastichsearchEngine, 'askput_mapping')
    @patch.object(ElastichsearchEngine, 'set_number_of_replicas')
    def test_put_mappings_calls_askput_when_mappings_match_not(self,
                                                               mock_set_number_of_replicas,
                                                               mock_askput_mapping,
                                                               mock_mapping_match,
                                                               mock_check_index_exists):
        mock_mapping_match.return_value = False
        self.es_manager.put_mappings(self.test_mappings)
        self.assertEquals(mock_askput_mapping.call_count, 3)

    @patch.object(ElastichsearchEngine, 'proceed')
    @patch.object(ElastichsearchEngine, 'delete_type')
    @patch.object(ElastichsearchEngine, 'put_mapping')
    @patch.object(ElastichsearchEngine, 'set_number_of_replicas')
    def test_askput_calls_delete_and_put_mappings_when_always_yes_and_erase(self,
                                                                            mock_set_number_of_replicas,
                                                                            mock_put_mapping,
                                                                            mock_delete_type,
                                                                            mock_proceed):
        self.mock_args.yes = True
        self.mock_args.erase = True
        mock_put_mapping.side_effect = [MergeMappingException('regular test failure'), 0]
        res = self.es_manager.askput_mapping('jobs', self.test_mappings['jobs'])
        self.assertTrue(mock_put_mapping.called)
        mock_delete_type.assert_called_once_with('jobs')

    def test_askput_does_nothing_when_test_only(self):
        self.mock_args.test_only = True
        res = self.es_manager.askput_mapping('jobs', self.test_mappings['jobs'])
        self.assertEquals(None, res)


    @patch('freezer_api.cmd.db_init.requests')
    def test_mapping_match_not_found_returns_false(self, mock_requests):
        self.mock_resp.status_code = 404
        mock_requests.codes.OK = 200
        mock_requests.codes.NOT_FOUND = 404
        mock_requests.get.return_value = self.mock_resp
        res = self.es_manager.mapping_match('jobs', self.test_mappings['jobs'])
        self.assertFalse(res)

    @patch('freezer_api.cmd.db_init.requests')
    def test_mapping_match_raises_Exception_on_response_not_in_200_404(self, mock_requests):
        self.mock_resp.status_code = 500
        mock_requests.get.return_value = self.mock_resp
        mock_requests.codes.OK = 200
        mock_requests.codes.NOT_FOUND = 404
        self.assertRaises(Exception, self.es_manager.mapping_match,
                          'jobs', self.test_mappings['jobs'])

    @patch('freezer_api.cmd.db_init.requests')
    def test_mapping_match_return_true_when_mapping_matches(self, mock_requests):
        self.mock_resp.status_code = 200
        self.mock_resp.json.return_value = {"freezerindex": {"mappings": {"jobs": {"properties": {"job_id": {"type": "string"}}}}}}
        mock_requests.get.return_value = self.mock_resp
        mock_requests.codes.OK = 200
        mock_requests.codes.NOT_FOUND = 404
        res = self.es_manager.mapping_match('jobs', self.test_mappings['jobs'])
        self.assertTrue(res)

    @patch('freezer_api.cmd.db_init.requests')
    def test_mapping_match_return_false_when_mapping_matches_not(self, mock_requests):
        self.mock_resp.status_code = 200
        self.mock_resp.text = '{"freezerindex": {"mappings": {"jobs":{"properties": {"job_id": {"type": "balloon"}}}}}}'
        mock_requests.get.return_value = self.mock_resp
        mock_requests.codes.OK = 200
        mock_requests.codes.NOT_FOUND = 404
        res = self.es_manager.mapping_match('jobs', self.test_mappings['jobs'])
        self.assertFalse(res)

    @patch('freezer_api.cmd.db_init.requests')
    def test_delete_type_returns_none_on_success(self, mock_requests):
        self.mock_resp.status_code = 200
        mock_requests.codes.OK = 200
        mock_requests.codes.NOT_FOUND = 404
        mock_requests.delete.return_value = self.mock_resp
        res = self.es_manager.delete_type('jobs')
        self.assertIsNone(res)

    @patch('freezer_api.cmd.db_init.requests')
    def test_delete_type_raises_Exception_on_response_code_not_200(self, mock_requests):
        self.mock_resp.status_code = requests.codes.BAD_REQUEST
        mock_requests.delete.return_value = self.mock_resp
        mock_requests.codes.OK = 200
        mock_requests.codes.BAD_REQUEST = 400
        mock_requests.codes.NOT_FOUND = 404
        self.assertRaises(Exception, self.es_manager.delete_type, 'jobs')

    @patch('freezer_api.cmd.db_init.requests')
    def test_put_mapping_returns_none_on_success(self, mock_requests):
        self.mock_resp.status_code = 200
        mock_requests.put.return_value = self.mock_resp
        mock_requests.codes.OK = 200
        mock_requests.codes.NOT_FOUND = 404
        res = self.es_manager.put_mapping('jobs', self.test_mappings['jobs'])
        self.assertIsNone(res)
        url = 'http://test:9333/freezerindex/_mapping/jobs'
        data = '{"properties": {"job_id": {"type": "string"}}}'
        mock_requests.put.assert_called_with(url, data=data)

    @patch('freezer_api.cmd.db_init.requests')
    def test_put_mapping_raises_Exception_on_response_code_not_200(self, mock_requests):
        self.mock_resp.status_code = 500
        mock_requests.put.return_value = self.mock_resp
        mock_requests.codes.OK = 200
        mock_requests.codes.NOT_FOUND = 404
        self.assertRaises(Exception, self.es_manager.put_mapping, 'jobs', self.test_mappings['jobs'])

    def test_proceed_returns_true_on_user_y(self):
        with patch('__builtin__.raw_input', return_value='y') as _raw_input:
            res = self.es_manager.proceed('fancy a drink ?')
            self.assertTrue(res)
            _raw_input.assert_called_once_with('fancy a drink ?')

    def test_proceed_returns_false_on_user_n(self):
        with patch('__builtin__.raw_input', return_value='n') as _raw_input:
            res = self.es_manager.proceed('are you drunk ?')
            self.assertFalse(res)
            _raw_input.assert_called_once_with('are you drunk ?')

    def test_proceed_returns_true_when_always_yes(self):
        res = self.es_manager.proceed('ask me not', True)
        self.assertTrue(res)

    @patch('freezer_api.cmd.db_init.requests')
    def test_check_index_exists_ok_when_index_exists(self, mock_requests):
        self.mock_resp.status_code = 200
        mock_requests.post.return_value = self.mock_resp
        mock_requests.codes.OK = 200
        mock_requests.codes.BAD_REQUEST = 400
        res = self.es_manager.check_index_exists()
        self.assertEquals(res, None)

    @patch('freezer_api.cmd.db_init.requests')
    def test_check_index_exists_ok_when_index_not_exists(self, mock_requests):
        self.mock_resp.status_code = 400
        mock_requests.post.return_value = self.mock_resp
        mock_requests.codes.OK = 200
        mock_requests.codes.BAD_REQUEST = 400
        res = self.es_manager.check_index_exists()
        self.assertEquals(res, None)


    @patch('freezer_api.cmd.db_init.requests')
    def test_check_index_raises_Exception_when_return_code_not_in_OK_BADREQ(self, mock_requests):
        self.mock_resp.status_code = 500
        mock_requests.post.return_value = self.mock_resp
        mock_requests.codes.OK = 200
        mock_requests.codes.BAD_REQUEST = 400
        self.assertRaises(Exception, self.es_manager.check_index_exists)

    def test_set_number_of_replicas_returns_none_on_match(self):
        self.es_manager.number_of_replicas_match = Mock()
        self.es_manager.number_of_replicas_match.return_value = True
        res = self.es_manager.set_number_of_replicas(5)
        self.assertEquals(res, None)

    def test_set_number_of_replicas_calls_askput_when_match_not(self):
        self.es_manager.number_of_replicas_match = Mock()
        self.es_manager.askput_number_of_replicas = Mock()
        self.es_manager.number_of_replicas_match.return_value = False
        res = self.es_manager.set_number_of_replicas(5)
        self.es_manager.askput_number_of_replicas.assert_called_once_with(5)
        self.assertEquals(res, None)

    @patch('freezer_api.cmd.db_init.requests')
    def test_number_of_replicas_match_returns_true_when_match(self, mock_requests):
        self.mock_resp.status_code = 200
        self.mock_resp.json.return_value = {"freezerindex": {
            "settings": {
                "index": {
                    "creation_date": "1447167673951",
                    "number_of_replicas": "3",
                    "number_of_shards": "5",
                    "uuid": "C63kkECBS4KXNPs-KKysPQ",
                    "version": {
                        "created": "1040299"
                    }
                }
            }}}
        mock_requests.get.return_value = self.mock_resp
        mock_requests.codes.OK = 200
        res = self.es_manager.number_of_replicas_match(3)
        self.assertTrue(res)

    @patch('freezer_api.cmd.db_init.requests')
    def test_number_of_replicas_match_returns_false_when_match_not(self, mock_requests):
        self.mock_resp.status_code = 200
        self.mock_resp.json.return_value = {"freezerindex": {
            "settings": {
                "index": {
                    "creation_date": "1447167673951",
                    "number_of_replicas": "3",
                    "number_of_shards": "5",
                    "uuid": "C63kkECBS4KXNPs-KKysPQ",
                    "version": {
                        "created": "1040299"
                    }
                }
            }}}
        mock_requests.get.return_value = self.mock_resp
        mock_requests.codes.OK = 200
        res = self.es_manager.number_of_replicas_match(4)
        self.assertFalse(res)

    def test_askput_number_of_replicas_sets_error_when_test_only(self):
        self.mock_args.test_only = True
        res = self.es_manager.askput_number_of_replicas(4)
        self.assertIsNone(res)
        self.assertEquals(self.es_manager.exit_code, os.EX_DATAERR)

    def test_askput_number_of_replicas_returns_none_when_no_proceed(self):
        self.mock_args.test_only = False
        self.es_manager.proceed = Mock()
        self.es_manager.proceed.return_value = False
        res = self.es_manager.askput_number_of_replicas(4)
        self.assertIsNone(res)
        self.assertEquals(self.es_manager.exit_code, os.EX_OK)

    @patch('freezer_api.cmd.db_init.requests')
    def test_askput_number_of_replicas_uses_correct_number(self, mock_requests):
        self.mock_args.test_only = False
        self.es_manager.proceed = Mock()
        self.es_manager.proceed.return_value = True
        self.mock_resp.status_code = 200
        mock_requests.codes.OK = 200
        mock_requests.put.return_value = self.mock_resp
        res = self.es_manager.askput_number_of_replicas(4)
        self.assertIsNone(res)
        mock_requests.put.assert_called_once_with('http://test:9333/freezerindex/_settings',
                                                  data=json.dumps({"number_of_replicas": 4}))
        self.assertEquals(self.es_manager.exit_code, os.EX_OK)

    @patch('freezer_api.cmd.db_init.requests')
    def test_askput_number_of_replicas_raises_NumberOfReplicasException_on_request_error(self, mock_requests):
        self.mock_args.test_only = False
        self.es_manager.proceed = Mock()
        self.es_manager.proceed.return_value = True
        self.mock_resp.status_code = 500
        mock_requests.codes.OK = 200
        mock_requests.put.return_value = self.mock_resp
        self.assertRaises(NumberOfReplicasException, self.es_manager.askput_number_of_replicas, 4)


class TestDbInit(unittest.TestCase):

    def setUp(self):
        self.mock_args = Mock()
        self.mock_args.test_only = False
        self.mock_args.always_yes = False
        self.mock_args.verbose = 1
        self.mock_args.select_mapping = ''
        self.mock_args.erase = False
        self.mock_args.replicas = 9

    @patch('freezer_api.cmd.db_init.argparse.ArgumentParser')
    def test_get_args_calls_add_argument(self, mock_ArgumentParser):
        mock_arg_parser = Mock()
        mock_ArgumentParser.return_value = mock_arg_parser

        retval = get_args([])
        call_count = mock_arg_parser.add_argument.call_count
        self.assertGreater(call_count, 6)

    @patch('freezer_api.cmd.db_init.os.path.isfile')
    @patch('freezer_api.cmd.db_init.os.getcwd')
    def test_find_config_file_returns_file_in_cwd(self, mock_os_getcwd, mock_os_path_isfile):
        mock_os_getcwd.return_value = '/home/woohoo'
        mock_os_path_isfile.return_value = True
        res = find_config_file()
        self.assertEquals('/home/woohoo/freezer-api.conf', res)

    @patch('freezer_api.cmd.db_init.os.path.isfile')
    @patch('freezer_api.cmd.db_init.os.getcwd')
    def test_find_config_file_returns_defaultfile(self, mock_os_getcwd, mock_os_path_isfile):
        mock_os_getcwd.return_value = '/home/woohoo'
        mock_os_path_isfile.side_effect = [False, True, False]
        res = find_config_file()
        self.assertEquals(DEFAULT_CONF_PATH, res)

    @patch('freezer_api.cmd.db_init.ConfigParser.ConfigParser')
    def test_parse_config_file_return_config_file_params(self, mock_ConfigParser):
        mock_config = Mock()
        mock_ConfigParser.return_value = mock_config
        mock_config.get.side_effect = lambda *x: {('storage', 'endpoint'): 'http://iperuranio:1999',
                                                  ('storage', 'index'): 'ohyes',
                                                  ('storage', 'number_of_replicas'): '10'}[x]
        host, port, index, replicas = parse_config_file('dontcare')
        self.assertEquals(host, 'iperuranio')
        self.assertEquals(port, 1999)
        self.assertEquals(index, 'ohyes')
        self.assertEquals(replicas, 10)

    def test_parse_config_file_return_False_values_when_no_config_fname(self):
        host, port, index, replicas = parse_config_file(None)
        self.assertEquals(host, None)
        self.assertEquals(port, 0)
        self.assertEquals(index, None)
        self.assertEquals(replicas, 0)

    @patch('freezer_api.cmd.db_init.parse_config_file')
    def test_get_db_params_returns_args_parameters(self, mock_parse_config_file):
        mock_parse_config_file.return_value = (None, None, None, None   )
        mock_args = Mock()
        mock_args.host = 'pumpkin'
        mock_args.port = 12345
        mock_args.index = 'ciccio'
        elasticsearch_url, elasticsearch_index, elasticsearch_replicas = get_db_params(mock_args)
        self.assertEquals(elasticsearch_url, 'http://pumpkin:12345')
        self.assertEquals(elasticsearch_index, 'ciccio')

    @patch('freezer_api.cmd.db_init.ElastichsearchEngine')
    @patch('freezer_api.cmd.db_init.get_db_params')
    @patch('freezer_api.cmd.db_init.get_args')
    def test_main_calls_esmanager_put_mappings_with_mappings(self, mock_get_args, mock_get_db_params,
                                                             mock_ElastichsearchEngine):
        mock_get_args.return_value = self.mock_args
        mock_get_db_params.return_value = 'url', 'index', 0
        mock_es_manager = Mock()
        mock_es_manager.exit_code = os.EX_OK

        mock_ElastichsearchEngine.return_value = mock_es_manager

        res = main()
        self.assertEquals(res, os.EX_OK)
        mappings = db_mappings.get_mappings()
        mock_es_manager.put_mappings.assert_called_with(mappings)

    @patch('freezer_api.cmd.db_init.ElastichsearchEngine')
    @patch('freezer_api.cmd.db_init.get_db_params')
    @patch('freezer_api.cmd.db_init.get_args')
    def test_main_return_EX_DATAERR_exitcode_on_error(self, mock_get_args, mock_get_db_params,
                                                    mock_ElastichsearchEngine):
        mock_get_args.return_value = self.mock_args
        mock_get_db_params.return_value = 'url', 'index', 0
        mock_es_manager = Mock()
        mock_ElastichsearchEngine.return_value = mock_es_manager

        mock_es_manager.put_mappings.side_effect = Exception('test error')

        res = main()
        self.assertEquals(res, os.EX_DATAERR)
