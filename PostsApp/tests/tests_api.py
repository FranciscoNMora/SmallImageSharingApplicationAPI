import io
import os
from pathlib import Path
from typing import Dict, Union

from PIL import Image
from django.conf import settings
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from PostsApp.models import Post
from PostsApp.tests.base_test import BaseTest


class APITests(BaseTest):
    def setUp(self):
        super().setUp()
        self.token1 = Token.objects.get(user=self.user1)
        self.token2 = Token.objects.get(user=self.user2)
        self.token3 = Token.objects.get(user=self.user3)
        self.auth_client1 = APIClient()
        self.auth_client2 = APIClient()
        self.auth_client3 = APIClient()
        self.unauth_client = APIClient()
        self.auth_client1.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        self.auth_client2.credentials(HTTP_AUTHORIZATION='Token ' + self.token2.key)
        self.auth_client3.credentials(HTTP_AUTHORIZATION='Token ' + self.token3.key)
        # Create MEDIA folder if does not exists
        try:
            os.makedirs(Path(settings.MEDIA_ROOT), exist_ok=True)
        except OSError as e:
            print(f"Error creating folder. Reason: {e}")

    def tearDown(self):
        self.auth_client1.logout()
        self.auth_client2.logout()
        self.auth_client3.logout()

        # Delete uploaded images
        media_path = Path(settings.MEDIA_ROOT)
        if media_path.is_dir():
            for filename in os.listdir(media_path):
                file_path = os.path.join(media_path, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                except OSError as e:
                    print(f'Failed to delete {file_path}. Reason: {e}')

    @staticmethod
    def _generate_picture_file():
        file = io.BytesIO()
        image = Image.new('RGBA', size=(100, 100), color=(155, 0, 0))
        image.save(file, 'png')
        file.name = 'test.png'
        file.seek(0)
        return file

    def _test_get_api_data(self, user: APIClient, url: str, status_code: int, number: int):
        resp = user.get(url)
        self.assertEqual(resp.status_code, status_code)
        self.assertEqual(len(resp.data), number)
        return resp.data

    def test_list_users(self):
        url = reverse('user-api-v1')
        resp = self.unauth_client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 3)
        for user in resp.data:
            self._test_keys(user, ['username', 'followers_number', 'following_number'])

    def test_create_user(self):
        url = reverse('user-api-v1')
        data: Dict[str, str] = {
            'username': 'username_test',
            'password': 'password_test'
        }
        resp = self.unauth_client.post(url, data, format='json')
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(User.objects.filter(username='username_test', profile__isnull=False).exists())

    def test_list_images(self):
        url = reverse('image-api-v1')
        self._test_get_api_data(self.auth_client1, url, 200, 0)
        data = self._test_get_api_data(self.auth_client2, url, 200, 3)
        self._test_get_api_data(self.auth_client3, url, 200, 0)
        for picture in data:
            self._test_keys(picture, ['caption', 'image', 'image_url'])
        self.assertEqual(data[0]['caption'], 'caption1')
        self.assertEqual(data[-1]['caption'], 'caption3')

    def test_list_images_unauthenticated_user(self):
        url = reverse('image-api-v1')
        resp = self.unauth_client.get(url)
        self.assertEqual(resp.status_code, 401)

    def test_list_post(self):
        url = reverse('post-api-v1')
        data = self._test_get_api_data(self.auth_client2, url, 200, 3)
        for post in data:
            self._test_keys(post, ['post_ref', 'created', 'created_timestamp', 'author', 'caption', 'image', 'image_url'])
        self.assertEqual(data[0]['caption'], 'caption2')
        self.assertEqual(data[-1]['caption'], 'caption3')

    def test_list_post_unauthenticated_user(self):
        url = reverse('post-api-v1')
        resp = self.unauth_client.get(url)
        self.assertEqual(resp.status_code, 401)

    def test_create_post(self):
        url = reverse('post-api-v1')
        picture_file = self._generate_picture_file()
        data: Dict[str, Union[str, Image]] = {
            'caption': 'caption4',
            'image': picture_file
        }
        resp = self.auth_client1.post(url, data, format='multipart')
        self.assertEqual(resp.status_code, 201, resp.data)
        self.assertTrue(Post.objects.filter(caption='caption4').exists())

    def test_follow_user(self):
        url = reverse('user-follow-api-v1')
        self.assertFalse(self.user3.profile.follows(self.user1))
        resp = self.auth_client3.put(url, {'username': 'user_1'})
        self.assertEqual(resp.status_code, 200, resp.data)
        self.assertTrue(self.user3.profile.follows(self.user1))

    def test_follow_user_unauthenticated_user(self):
        url = reverse('user-follow-api-v1')
        resp = self.unauth_client.put(url, {'username': 'user_1'})
        self.assertEqual(resp.status_code, 401)

    def test_unfollow_user(self):
        url = reverse('user-follow-api-v1')
        self.assertTrue(self.user1.profile.follows(self.user3))
        resp = self.auth_client1.delete(url, {'username': 'user_3'})
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(self.user1.profile.follows(self.user3))

    def test_unfollow_user_unauthenticated_user(self):
        url = reverse('user-follow-api-v1')
        resp = self.unauth_client.delete(url, {'username': 'user_1'})
        self.assertEqual(resp.status_code, 401)

    def test_follow_user_same_user(self):
        url = reverse('user-follow-api-v1')
        resp = self.auth_client1.put(url, {'username': 'user_1'})
        self.assertEqual(resp.status_code, 400)

    def test_like_post(self):
        url = reverse('post-like-api-v1')
        self.assertFalse(self.user3.profile.likes(self.post1))
        resp = self.auth_client3.put(url, {'post_ref': self.post1.post_ref})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(self.user3.profile.likes(self.post1))

    def test_unlike_post(self):
        url = reverse('post-like-api-v1')
        self.assertTrue(self.user2.profile.likes(self.post1))
        resp = self.auth_client2.delete(url, {'post_ref': self.post1.post_ref})
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(self.user2.profile.likes(self.post1))

    def test_like_own_post(self):
        url = reverse('post-like-api-v1')
        self.assertTrue(self.user2.profile.likes(self.post1))
        resp = self.auth_client1.put(url, {'post_ref': self.post1.post_ref})
        self.assertEqual(resp.status_code, 400)
