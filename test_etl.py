import requests
from etl.ex_dsg_db_pull import pull_index
import pytest
import pandas as pd
from etl.tr_jqa_network import create_adj_matrix

class TestAPIScript():
    def test_api_call_success(self, mocker):
        ''' test for successful api call '''
        # Mock requests.get
        mock_get = mocker.patch("etl.ex_dsg_db_pull.requests.get")

        # Create a mock response with a 200 status code
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.text = "<response><key>value</key></response>" 
        mock_get.return_value = mock_response

        url = "jqa"
        result = pull_index(url, {'username': 'abc', 'password': 'xyz'})
        # Check that the function handles the mock response correctly
        assert isinstance(result, str)  # test if result is string
        assert "<key>value</key>" in result  # Check if the key exists in the result
        # Verify that requests.get was called
        mock_get.assert_called_once_with(f'https://dsg.xmldb-dev.northeastern.edu/basex/rest/psc/{url}', auth=('abc', 'xyz'), timeout=10)

    def test_api_call_failure(self, mocker):
        ''' test for unsuccessful api call'''
        # Mock requests.get
        mock_get = mocker.patch("etl.ex_dsg_db_pull.requests.get")

        # Create a mock response with a 404 status code 
        mock_response = mocker.Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Client Error")
        mock_get.return_value = mock_response
        url = "jqa"
        with pytest.raises(requests.exceptions.HTTPError, match="404 Client Error"):
            pull_index(url, {'username': 'abc', 'password': 'xyz'})
        # Verify that requests.get was called
        mock_get.assert_called_once_with(f'https://dsg.xmldb-dev.northeastern.edu/basex/rest/psc/{url}', auth=('abc', 'xyz'), timeout=10)

