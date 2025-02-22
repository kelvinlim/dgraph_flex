import unittest
import io
from unittest.mock import patch
from dgraph_flex import DgraphFlex  # Import from the package

class TestReadYaml(unittest.TestCase):
    
    @patch('dgraph_flex.open', create=True)  # Mock the 'open' function
    def test_valid_version(self, mock_open):
        # Prepare mock YAML data with a valid version
        mock_yaml_data = """
        GENERAL:
            version: 1.0
        """
        mock_open.return_value.__enter__.return_value = io.StringIO(mock_yaml_data)

        # Create an instance of your class
        instance = DgraphFlex()
        instance.yamlpath = 'test_config.yaml'  # Set the YAML file path

        # Call the read_yaml method
        result = instance.read_yaml(version=1.0)

        # Assertions
        self.assertEqual(result['GENERAL']['version'], 1.0)  # Check if the version is correct
        #... (Test methods as described in the previous response)...