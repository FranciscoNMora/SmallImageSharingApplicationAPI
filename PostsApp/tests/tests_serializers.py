from django.contrib.auth.models import User

from PostsApp.models import Post
from PostsApp.serializers import UserSerializer, ImageSerializer, PostSerializer
from PostsApp.tests.base_test import BaseTest


class UserSerializerTests(BaseTest):
    def test_users_serializer_keys(self):
        for user in UserSerializer(User.objects.all(), many=True).data:
            self._test_keys(user, ['username', 'followers_number', 'following_number'], exclude=['password'])

    def test_users_serializer_values(self):
        self._test_values(UserSerializer(self.user1).data,
                          {'username': 'user_1', 'followers_number': 1, 'following_number': 1})
        self._test_values(UserSerializer(self.user2).data,
                          {'username': 'user_2', 'followers_number': 0, 'following_number': 2})
        self._test_values(UserSerializer(self.user3).data,
                          {'username': 'user_3', 'followers_number': 2, 'following_number': 0})


class PictureSerializerTests(BaseTest):
    def test_images_serializer_keys(self):
        for image in ImageSerializer(Post.objects.all(), many=True).data:
            self._test_keys(image, ['caption', 'image', 'image_url'])

    def test_images_serializer_values(self):
        self._test_values(ImageSerializer(self.post1).data,
                          {'caption': 'caption1', 'image': '/media/image_1.png', 'image_url': '/media/image_1.png'})
        self._test_values(ImageSerializer(self.post2).data,
                          {'caption': 'caption2', 'image': '/media/image_2.png', 'image_url': '/media/image_2.png'})
        self._test_values(ImageSerializer(self.post3).data,
                          {'caption': 'caption3', 'image': '/media/image_3.png', 'image_url': '/media/image_3.png'})


class PostSerializerTests(BaseTest):
    def test_posts_serializer(self):
        for post in PostSerializer(Post.objects.all(), many=True).data:
            self._test_keys(post,
                            ['post_ref', 'created', 'created_timestamp', 'author', 'caption', 'image', 'image_url'])

    def test_images_serializer_values(self):
        self._test_values(PostSerializer(self.post1).data,
                          {'post_ref': '70e8a23e-4873-4961-83aa-9e780d3902e1', 'created': '2020-10-21 13:10:08+0000',
                           'created_timestamp': 1603285808, 'author': 2, 'caption': 'caption1',
                           'image': '/media/image_1.png', 'image_url': '/media/image_1.png'})
        self._test_values(PostSerializer(self.post2).data,
                          {'post_ref': '7787fc71-72c9-4ecf-a5a8-7d2642589ff6', 'created': '2020-10-21 13:12:14+0000',
                           'created_timestamp': 1603285934, 'author': 2, 'caption': 'caption2',
                           'image': '/media/image_2.png', 'image_url': '/media/image_2.png'}
                          )
        self._test_values(PostSerializer(self.post3).data,
                          {'post_ref': 'f2d3e4ac-cc77-4471-b898-6b1031ab9dfa', 'created': '2020-10-21 13:21:46+0000',
                           'created_timestamp': 1603286506, 'author': 2, 'caption': 'caption3',
                           'image': '/media/image_3.png', 'image_url': '/media/image_3.png'}
                          )
