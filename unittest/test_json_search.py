# Fill the Python code in this file
import unittest 
from recursive_json_search import * 
from test_data import * 
 
class json_search_test(unittest.TestCase): 
    '''test module to test search function in 
`recursive_json_search.py`''' 
    def test_search_found(self): 
        '''key should be found, return list should not be empty''' 
        self.assertTrue([]!=json_search(key1,data)) 
    def test_search_not_found(self): 
        '''key should not be found, should return an empty list''' 
        self.assertTrue([]==json_search(key2,data)) 
    def test_is_a_list(self): 
        '''Should return a list''' 
        self.assertIsInstance(json_search(key1,data),list) 

    def test_viewer_cannot_read_api_key(self):
        """Viewer must not be allowed to read apiKey."""
        result = json_search("apiKey", data, role="viewer")
        self.assertEqual([], result)

    def test_viewer_cannot_read_management_ip(self):
        """Viewer must not be allowed to read managementIpAddress."""
        result = json_search(
            "managementIpAddress",
            data,
            role="viewer"
        )
        self.assertEqual([], result)

    def test_admin_can_read_api_key(self):
        """Admin should be allowed to read apiKey."""
        result = json_search("apiKey", data, role="admin")
        self.assertNotEqual([], result)
 
if __name__ == '__main__': 
    unittest.main() 
