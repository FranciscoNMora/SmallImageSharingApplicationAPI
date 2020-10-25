from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework import mixins, generics, permissions, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView

from PostsApp.app_utils.views_utils import ErrorResponse
from PostsApp.models import Post, LikeException, FollowException
from PostsApp.serializers import ImageSerializer, PostSerializer, UserSerializer


# API requirements
#   1. Images have a caption, limited to 100 chars.
#   2. A user can follow/unfollow another user.
#   3. Current user can like a post (image).
#   4. List of images for the current user (most recent first, limited to users following).
#   5. List of all posts (ordered by likes).
#   6. List of all users (including information on the number of following and followers).

class PostListAPI(mixins.ListModelMixin, generics.GenericAPIView):
    parser_classes = (FormParser, MultiPartParser)
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Post.objects.all().annotate(number_likes=Count('liked')).order_by('-number_likes')
    serializer_class = PostSerializer

    def get(self, request, *args, **kwargs):
        """
        List of all posts (ordered by likes)
        """
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Creates a new post with an image.
        The 'author' of the Post will be the logged user of the API, and the 'post_ref' code is
        generated automatically in DB, so this values are not necessary in the form.
        """
        serializer = self.serializer_class(data=request.data, context={'author': request.user.pk})
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


post_ref_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'post_ref': openapi.Schema(type=openapi.TYPE_STRING, description='Post reference id'),
    }
)


class PostLikeAPI(APIView):
    """
    This API allows to a logged User to like/unlike a Post
    """
    permission_classes = (permissions.IsAuthenticated,)

    @swagger_auto_schema(request_body=post_ref_schema, operation_description='Like a Post',
                         responses={200: 'Post liked', 400: 'Post belongs to user', 404: 'Post does not exists'})
    def put(self, request, *args, **kwargs):
        try:
            post_ref: str = request.data["post_ref"]
            post: Post = get_object_or_404(Post, post_ref=post_ref)
            request.user.profile.like_post(post)
        except LikeException:
            return ErrorResponse(status.HTTP_400_BAD_REQUEST, "Post belongs to user")

        return Response(status.HTTP_200_OK)

    @swagger_auto_schema(request_body=post_ref_schema, operation_description='Unlike a Post',
                         responses={200: 'Post liked', 404: 'Post does not exists'})
    def delete(self, request, *args, **kwargs):
        try:
            post_ref: str = request.data["post_ref"]
            post: Post = get_object_or_404(Post, post_ref=post_ref)
            request.user.profile.unlike_post(post)
        except LikeException:
            return ErrorResponse(status.HTTP_400_BAD_REQUEST, "Post belongs to user")

        return Response(status.HTTP_200_OK)


class ImageListAPI(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ImageSerializer

    def get_queryset(self):
        """
        List of images for the current user (most recent first, limited to users following).
        """
        user: User = self.request.user
        following_users = user.profile.following.all()
        return Post.objects.filter(author__in=following_users).order_by('created')


class UserListAPI(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  generics.GenericAPIView):
    parser_classes = (JSONParser, FormParser,)
    queryset = User.objects.filter(profile__isnull=False)
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        """
        List of all users (including information on the number of following and followers)
        """
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Creates new user
        """
        return self.create(request, *args, **kwargs)


username_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'username': openapi.Schema(type=openapi.TYPE_STRING, description='User to like username'),
    }
)


class UserFollowAPI(APIView):
    """
    Follow/unfollow user
    """
    permission_classes = (permissions.IsAuthenticated,)

    @swagger_auto_schema(request_body=username_schema, operation_description='Follow an User',
                         responses={200: 'User followed', 400: 'User can not follow himself',
                                    404: 'User does not exists'})
    def put(self, request, *args, **kwargs):
        try:
            user_name: str = request.data["username"]
            user: User = get_object_or_404(User, username=user_name)
            request.user.profile.follow_user(user)
        except FollowException:
            return ErrorResponse(status.HTTP_400_BAD_REQUEST, "User can not follow himself")

        return Response(status.HTTP_200_OK)

    @swagger_auto_schema(request_body=username_schema, operation_description='Unfollow an User',
                         responses={200: 'User followed',
                                    404: 'User does not exists'})
    def delete(self, request, *args, **kwargs):
        user_name: str = request.data["username"]
        user: User = get_object_or_404(User, username=user_name)
        request.user.profile.unfollow_user(user)

        return Response(status.HTTP_200_OK)
