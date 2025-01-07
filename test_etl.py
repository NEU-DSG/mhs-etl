import requests
from etl.ex_dsg_db_pull import pull_index
import pytest
import pandas as pd
from etl.tr_jqa_network import create_adj_matrix
from etl.tr_subject_headings import subjects_by_year

# @pytest.fixture(scope="module")
# def global_rbt_cms_data():
#     # Create global data here
#     return pd.DataFrame({
#         'file': ['CMS00144.xml', 'CMS00193.xml', 'CMS00187.xml'],
#         'date': ['1828-02-05', '1822-10-07', '1822-08-16'],
#         'source': ['sedgwick-catharine', 'sedgwick-catharine', 'sedgwick-catharine'],
#         'target': ['sedgwick-charles', 'follen-eliza', 'channing-susan'],
#         'subjects': ['Family Relations (Sedgwick Family)|Childbirth|Pregnancy|Health and Illness|Shopping and Material Exchange|Work|Education|Literature and History|Reform Movements|Social Life and Networks|Religion|Self-reflection|Bible|Family Finances (Sedgwick Family)|Leisure Activities|Gender Roles', 'Family Relations (Sedgwick Family)|Religion|Social Life and Networks|Friendship|Childhood|Unitarianism|Gifts|Bible|Recreation|Village Life|Natural World', 'Social Life and Networks|Authorship|Religion|Unitarianism|Friendship|Village Life|Death|Motherhood|Gender Roles|Health and Illness|Childbirth'],
#         'references': ['edgwick-henry,ladd-william,mason-john6,bayard-william,constostavlos-alexander,minot-katharine,sedgwick-elizabeth,sedgwick-elizabeth2', 'greenwood-francis,minot-katharine,sedgwick-charles,sedgwick-elizabeth,sedgwick-jane,channing-susan,channing-williamh', 'field-submit,field-david,follen-eliza,lyman-anne,cabot-susan,channing-william,channing-barbara,unknown-mary-cms,u,sparks-jared'],
#         'text': ['a', 'b', 'c']
#     })

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

class TestSubject():
    @pytest.fixture
    def df_incorrect_date(self):
        return pd.DataFrame({
        'file': ['CMS00144.xml'],
        'date': ['1828-02'],
        'source': ['sedgwick-catharine'],
        'target': ['sedgwick-charles'],
        'subjects': ['Family Relations (Sedgwick Family)'],
        'references': ['edgwick-henry,ladd-william,mason-john6,bayard-william,constostavlos-alexander,minot-katharine,sedgwick-elizabeth,sedgwick-elizabeth2'],
        'text': ['a']
    })

    @pytest.fixture
    def df_sample(self):
        return pd.DataFrame({
        'file': ['RBT01814.xml', 'RBT01814.xml', 'RBT01814.xml'],
        'date': ['1828-02-05', '1828-02-05', '1828-02-05'],
        'source': ['taney-roger-brooke', 'taney-roger-brooke', 'taney-roger-brooke'],
        'target': ['ellicott-thomas', 'ellicott-thomas', 'ellicott-thomas'],
        'subjects': ['Privacy', 'Transfer Drafts', 'Treasury Department'],
        'references': ['edgwick-henry,ladd-william,mason-john6,bayard-william,constostavlos-alexander,minot-katharine,sedgwick-elizabeth,sedgwick-elizabeth2', 'greenwood-francis,minot-katharine,sedgwick-charles,sedgwick-elizabeth,sedgwick-jane,channing-susan,channing-williamh', 'field-submit,field-david,follen-eliza,lyman-anne,cabot-susan,channing-william,channing-barbara,unknown-mary-cms,u,sparks-jared'],
        'text': ['a', 'b', 'c']
    })
    
    def test_incorrect_date(self, df_incorrect_date):
        subjects = subjects_by_year(df_incorrect_date)
        assert subjects.empty, "Expected empty when incorrect date."
        
    def test_expected(self, df_sample):
        expected_output = pd.DataFrame({
        'year': [1828, 1828, 1828],
        'subjects': ['Privacy', 'Transfer Drafts', 'Treasury Department'],
        'count': [1, 1, 1],
        'total': [3, 3, 3],
        'percentage': [33.0, 33.0, 33.0]
        })
        subjects = subjects_by_year(df_sample)
        pd.testing.assert_frame_equal(subjects.reset_index(drop=True), expected_output.reset_index(drop=True), check_dtype=False)



# class TestCreateAdjMatrix:

#     @pytest.fixture
#     def sample_data(self):
#         return pd.DataFrame({
#             'entry': ['A', 'B', 'C', 'D', 'E'],
#             'people': ['u', 'source', 'A', 'B', 'C'],
#             'date': ['1800-01-01', '1825-01-01', '1801-01-01', '1830-01-01', '1825-01-01']
#         })

#     @pytest.fixture
#     def df_no_connections(self):
#         return pd.DataFrame({
#             'entry': ['A', 'B', 'C', 'D', 'E'],
#             'people': ['A', 'B', 'C', 'D', 'E'],
#             'date': ['1800-01-01', '1825-01-01', '1801-01-01', '1830-01-01', '1825-01-01']
#         })
    
#     @pytest.fixture
#     def df_valid(self):
#         return pd.DataFrame({
#             'entry': ['A', 'A', 'B', 'B', 'C'],
#             'people': ['source', 'B', 'source', 'C', 'source'],
#             'date': ['1800-01-01', '1825-01-01', '1825-01-01', '1830-01-01', '1825-01-01']
#         })
    
#     def test_create_adj_matrix_empty(self):
#         # Test with an empty dataframe
#         df_empty = pd.DataFrame(columns=['entry', 'people', 'date'])
#         result = create_adj_matrix(df_empty, weight=1)
#         assert result.empty, "Expected empty DataFrame when input is empty"
    
#     def test_create_adj_matrix_no_connections(self, df_no_connections):
#         # Test when no connections meet the weight condition
#         result = create_adj_matrix(df_no_connections, weight=10)
#         assert result.empty, "Expected empty DataFrame when no connections meet the weight condition"
    
#     def test_create_adj_matrix_valid(self, df_valid):
#         # Test when valid connections exist
#         result = create_adj_matrix(df_valid, weight=1)
#         assert not result.empty, "Expected non-empty DataFrame when valid connections exist"
#         assert len(result) == 3, "Expected 3 edges in the result"
#         assert all(result['weight'] >= 1), "Expected all weights to be greater than or equal to the given threshold"
    
#     def test_query_filters(self):
#         # Test the query filters in the function
#         df_query_test = pd.DataFrame({
#             'entry': ['A', 'B', 'C', 'D', 'E'],
#             'people': ['A', 'B', 'source', 'source', 'A'],
#             'date': ['1800-01-01', '1825-01-01', '1830-01-01', '1825-01-01', '1800-01-01']
#         })
#         result = create_adj_matrix(df_query_test, weight=1)
#         # We expect 'source' as one of the columns but not as a target in any row
#         assert 'source' not in result['target'].values
    
#     def test_melt_and_dot(self):
#         # Test the correct conversion of the matrix via dot and melt functions
#         df_melt_dot = pd.DataFrame({
#             'entry': ['A', 'B', 'A', 'B'],
#             'people': ['C', 'C', 'D', 'D'],
#             'date': ['1800-01-01', '1825-01-01', '1800-01-01', '1825-01-01']
#         })
#         result = create_adj_matrix(df_melt_dot, weight=1)
#         # Check that dot operation worked correctly
#         assert 'source' in result.columns, "Expected 'source' in the result DataFrame"
