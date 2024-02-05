#!/usr/bin/env python3
""" Module for testing client """

from client import GithubOrgClient
from fixtures import TEST_PAYLOAD
from parameterized import parameterized, parameterized_class
import unittest
from unittest.mock import patch, PropertyMock


class TestGithubOrgClient(unittest.TestCase):
    """ Test class for GithubOrgClient """

    @parameterized.expand([
        ('google',),
        ('abc',)
    ])
    @patch('client.get_json')
    def test_org(self, org_name, mock_get_json):
        """Test that GithubOrgClient.org returns the correct value"""
        test_instance = GithubOrgClient(org_name)
        test_instance.org()
        mock_get_json.assert_called_once_with(f'https://api.github.com/orgs/{org_name}')

    def test_public_repos_url(self):
        """ Test that the result of _public_repos_url is as expected
        based on the mocked payload
        """
        with patch('client.GithubOrgClient.org',
                   new_callable=PropertyMock) as mock_org:
            payload = {"repos_url": "World"}
            mock_org.return_value = payload
            test_instance = GithubOrgClient('test')
            result = test_instance._public_repos_url
            self.assertEqual(result, payload["repos_url"])

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """
        Test that the list of repos is as expected from the chosen payload.
        Test that the mocked property and the mocked get_json was called once.
        """
        json_payload = [{"name": "Google"}, {"name": "Twitter"}]
        mock_get_json.return_value = json_payload

        with patch('client.GithubOrgClient._public_repos_url',
                   new_callable=PropertyMock) as mock_public_repos_url:

            mock_public_repos_url.return_value = "hello/world"
            test_instance = GithubOrgClient('test')
            result = test_instance.public_repos()

            expected_repo_names = [repo["name"] for repo in json_payload]
            self.assertEqual(result, expected_repo_names)

            mock_public_repos_url.assert_called_once()
            mock_get_json.assert_called_once()

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False)
    ])
    def test_has_license(self, repo, license_key, expected):
        """ unit-test for GithubOrgClient.has_license """
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)


@parameterized_class(
    ("org_payload", "repos_payload", "expected_repos", "apache2_repos"),
    TEST_PAYLOAD
)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """ Class for Integration test of fixtures """

    @classmethod
    def setUpClass(cls):
        """A class method called before tests in an individual class are run"""
        config = {'return_value.json.side_effect':
                  [
                      cls.org_payload, cls.repos_payload,
                      cls.org_payload, cls.repos_payload
                  ]
                  }
        cls.get_patcher = patch('requests.get', **config)
        cls.mock_get = cls.get_patcher.start()

    def test_public_repos(self):
        """ Integration test: public repos"""
        test_instance = GithubOrgClient("google")

        self.assertEqual(test_instance.org, self.org_payload)
        self.assertEqual(test_instance.repos_payload, self.repos_payload)
        self.assertEqual(test_instance.public_repos(), self.expected_repos)
        self.assertEqual(test_instance.public_repos("XLICENSE"), [])
        self.mock_get.assert_called()

    def test_public_repos_with_license(self):
        """ Integration test for public repos with License """
        test_instance = GithubOrgClient("google")

        self.assertEqual(test_instance.public_repos(), self.expected_repos)
        self.assertEqual(test_instance.public_repos("XLICENSE"), [])
        self.assertEqual(test_instance.public_repos(
            "apache-2.0"), self.apache2_repos)
        self.mock_get.assert_called()

    @classmethod
    def tearDownClass(cls):
        """A class method called after tests in an individual class have run"""
        cls.get_patcher.stop()
