"""
Unit tests for the Joke Generator
"""

import unittest
from unittest.mock import patch, MagicMock
from joke_generator import JokeGenerator


class TestJokeGenerator(unittest.TestCase):
    """Test cases for JokeGenerator class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.generator = JokeGenerator()
    
    @patch('joke_generator.requests.Session.get')
    def test_get_random_joke_success(self, mock_get):
        """Test successfully fetching a random joke"""
        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'type': 'single',
            'joke': 'Why did the developer go broke? Because he lost his domain in a bad divorce settlement.',
            'category': 'Programming'
        }
        mock_get.return_value = mock_response
        
        # Get joke
        joke = self.generator.get_random_joke()
        
        # Assertions
        self.assertIsNotNone(joke)
        self.assertEqual(joke['type'], 'single')
        self.assertIn('developer', joke['joke'].lower())
    
    @patch('joke_generator.requests.Session.get')
    def test_get_random_joke_with_safe_mode(self, mock_get):
        """Test fetching joke with safe mode enabled"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'type': 'single',
            'joke': 'Why do programmers prefer dark mode?',
            'category': 'General'
        }
        mock_get.return_value = mock_response
        
        joke = self.generator.get_random_joke(safe_mode=True)
        
        self.assertIsNotNone(joke)
        mock_get.assert_called_once()
    
    @patch('joke_generator.requests.Session.get')
    def test_get_random_joke_api_error(self, mock_get):
        """Test handling of API errors"""
        mock_get.side_effect = Exception("Connection error")
        
        joke = self.generator.get_random_joke()
        
        self.assertIsNone(joke)
    
    def test_display_joke_single_type(self, ):
        """Test displaying a single-type joke"""
        joke_data = {
            'type': 'single',
            'joke': 'Test joke',
            'category': 'Programming'
        }
        
        # This should not raise an exception
        try:
            self.generator.display_joke(joke_data)
        except Exception as e:
            self.fail(f"display_joke raised {type(e).__name__} unexpectedly!")
    
    def test_display_joke_twopart_type(self):
        """Test displaying a two-part joke"""
        joke_data = {
            'type': 'twopart',
            'setup': 'Why did the developer go broke?',
            'delivery': 'Because he lost his cache!',
            'category': 'Programming'
        }
        
        try:
            self.generator.display_joke(joke_data)
        except Exception as e:
            self.fail(f"display_joke raised {type(e).__name__} unexpectedly!")
    
    def test_display_joke_with_error(self):
        """Test displaying error response"""
        joke_data = {
            'error': True,
            'message': 'No jokes found'
        }
        
        try:
            self.generator.display_joke(joke_data)
        except Exception as e:
            self.fail(f"display_joke raised {type(e).__name__} unexpectedly!")
    
    @patch('joke_generator.requests.Session.get')
    def test_get_multiple_jokes(self, mock_get):
        """Test fetching multiple jokes"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'type': 'single',
            'joke': 'Test joke',
            'category': 'General'
        }
        mock_get.return_value = mock_response
        
        jokes = self.generator.get_multiple_jokes(count=3)
        
        self.assertEqual(len(jokes), 3)
        self.assertEqual(mock_get.call_count, 3)


if __name__ == '__main__':
    unittest.main()
