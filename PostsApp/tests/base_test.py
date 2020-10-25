from typing import Any, List, Dict

from django.test import TransactionTestCase

from django.contrib.auth.models import User

from PostsApp.models import Post


class BaseTest(TransactionTestCase):
    fixtures = ["tests.yaml"]

    def setUp(self) -> None:
        self.user1 = User.objects.get(username='user_1')
        self.user2 = User.objects.get(username='user_2')
        self.user3 = User.objects.get(username='user_3')
        self.post1 = Post.objects.get(post_ref='70e8a23e-4873-4961-83aa-9e780d3902e1')
        self.post2 = Post.objects.get(post_ref='7787fc71-72c9-4ecf-a5a8-7d2642589ff6')
        self.post3 = Post.objects.get(post_ref='f2d3e4ac-cc77-4471-b898-6b1031ab9dfa')

    def _test_keys(self, obj: Any, keys: List[str], *, exclude: List[str] = []):
        for key in keys:
            self.assertIn(key, obj)
        for key in exclude:
            self.assertNotIn(key, obj)

    def _test_values(self, obj: Dict[str, Any], expected: Dict[str, Any]):
        for key, value in expected.items():
            self.assertEqual(obj[key], expected[key])
