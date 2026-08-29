import unittest
from webhook_candidate import translate


class TestTranslate(unittest.TestCase):
    def setUp(self):
        self.valid_data = {
            'action': 'opened',
            'pull_request': {
                'number': 1,
                'title': 'Test PR',
                'user': {'login': 'testuser'},
                'head': {'ref': 'feature-branch'},
                'base': {'ref': 'main'},
                'created_at': '2023-10-01T00:00:00Z',
                'html_url': 'https://example.com/pr/1',
                'draft': False
            },
            'repository': {'full_name': 'test/repo'}
        }

    def test_valid_payload(self):
        result = translate(self.valid_data)
        expected = {
            'event_type': 'opened', 'pr_number': 1, 'title': 'Test PR',
            'description': None, 'author_login': 'testuser',
            'source_branch': 'feature-branch', 'target_branch': 'main',
            'repo_full_name': 'test/repo', 'draft': False,
            'created_at': '2023-10-01T00:00:00Z',
            'url': 'https://example.com/pr/1', 'labels': [], 'reviewers': []
        }
        self.assertEqual(result, expected)

    def test_missing_optional_fields(self):
        data = self.valid_data.copy()
        data['pull_request'].pop('body', None)
        data['pull_request']['labels'] = []
        data['pull_request']['requested_reviewers'] = []
        result = translate(data)
        self.assertIsNone(result['description'])
        self.assertEqual(result['labels'], [])
        self.assertEqual(result['reviewers'], [])

    def test_malformed_input_not_dict(self):
        with self.assertRaises(ValueError):
            translate('not a dictionary')

    def test_missing_required_field(self):
        data = self.valid_data.copy()
        del data['action']
        with self.assertRaises(ValueError):
            translate(data)

    def test_invalid_action(self):
        data = self.valid_data.copy()
        data['action'] = 'invalid'
        with self.assertRaises(ValueError):
            translate(data)

    def test_missing_nested_field(self):
        data = self.valid_data.copy()
        del data['pull_request']['user']['login']
        with self.assertRaises(ValueError):
            translate(data)

    def test_missing_pr_field(self):
        data = self.valid_data.copy()
        del data['pull_request']['title']
        with self.assertRaises(ValueError):
            translate(data)


if __name__ == '__main__':
    unittest.main()
