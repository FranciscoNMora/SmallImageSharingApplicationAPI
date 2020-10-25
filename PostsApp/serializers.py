from django.contrib.auth.models import User
from rest_framework import serializers

from PostsApp.app_utils.serializers_utils import UnixTimestampField
from PostsApp.models import Post


class ImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField('get_image_url', read_only=True)

    def get_image_url(self, obj: Post):
        return obj.image.url

    class Meta:
        model = Post
        fields = ('caption', 'image', 'image_url')


class PostSerializer(ImageSerializer):
    created = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S%z", read_only=True)
    created_timestamp = UnixTimestampField(source='created', read_only=True)

    class Meta:
        model = Post
        fields = ('post_ref', 'created', 'created_timestamp', 'author', 'caption', 'image', 'image_url')
        extra_kwargs = {
            'post_ref ': {'read_only': True},
            'author ': {'required': False},
        }

    def to_internal_value(self, data):
        data['author'] = self.context['author']
        return super(PostSerializer, self).to_internal_value(data)


class UserSerializer(serializers.ModelSerializer):
    followers_number = serializers.SerializerMethodField(read_only=True)
    following_number = serializers.SerializerMethodField(read_only=True)

    def get_followers_number(self, obj: User):
        return obj.profile.followers_number if hasattr(obj, 'profile') else None

    def get_following_number(self, obj: User):
        return obj.profile.following_number if hasattr(obj, 'profile') else None

    class Meta:
        model = User
        fields = ('username', 'followers_number', 'following_number', 'password')
        extra_kwargs = {'password': {'write_only': True}}

