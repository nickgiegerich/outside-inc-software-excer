from re import S
import unittest
from urllib.error import HTTPError

from driver import load_url, parse_document, build_urls


class TestLoadUrl(unittest.TestCase):
    def test_404_response(self):
        """ 
        Test that we get a 404 response on misspelled words
        """
        url = 'https://outside-interview.herokuapp.com/spelling/thts'
        try:
            load_url(url, 60)
        except HTTPError:
            pass
        except Exception:
            self.fail('unexpected excpetion')

    def test_204_response(self):
        """ 
        Test that we get a 204 response on misspelled words
        """
        url = "https://outside-interview.herokuapp.com/spelling/that's"
        request = load_url(url, 60)
        self.assertEqual(request, 204)


class TestParsingFunction(unittest.TestCase):
    def test_parsing_hypens(self):
        """ 
        Test that words with hyphens seperate into two words ex: super-duper => super duper 
        """
        string_to_test = 'these-words-should-be-separate'
        result = parse_document(string_to_test)
        self.assertEqual(
            result, ['these', 'words', 'should', 'be', 'separate'])

    def test_random_chars(self):
        """ 
        Test random characters that should be parsed
        """
        string_to_test = "it's about time we're needed, * elsewhere . & sometime; soon"
        result = parse_document(string_to_test)
        self.assertEqual(
            result, ["it's", 'about', 'time', "we're", 'needed', "elsewhere", 'sometime', 'soon'])


class TestUrlBuilder(unittest.TestCase):
    def test_build_url(self):
        """ 
        Test to make sure urls build properly
        """
        list_of_words = ['one', 'Two']
        result = build_urls(list_of_words)
        self.assertEqual(
            result,
            [
                'https://outside-interview.herokuapp.com/spelling/one',
                'https://outside-interview.herokuapp.com/spelling/Two'
            ]
        )


if __name__ == '__main__':
    unittest.main()
