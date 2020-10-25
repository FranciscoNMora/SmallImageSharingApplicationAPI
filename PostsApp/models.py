import uuid

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

from PostsApp.app_utils.exceptions import FollowException, LikeException
from PostsApp.app_utils.general_utils import disable_for_loaddata


class Profile(models.Model):
    """
    Extension for User model that contains the attributes and function necessary for an user to follow another, and
    also functions to like Posts.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    following = models.ManyToManyField(User, related_name='followers', blank=True)

    @property
    def following_number(self):
        """Number of Users that the owner of the profile follows"""
        return self.following.count()

    @property
    def followers_number(self):
        """Number of Users that follows the owner of the profile"""
        return self.user.followers.count()

    def follow_user(self, user: User) -> None:
        self.following.add(user)

    def unfollow_user(self, user: User) -> None:
        self.following.remove(user)

    def follows(self, user: User) -> bool:
        """Indicates if user is followed by the owner of the profle"""
        return user in self.following.all()

    def like_post(self, post: 'Post') -> None:
        post.liked.add(self.user)

    def unlike_post(self, post: 'Post') -> None:
        post.liked.remove(self.user)

    def likes(self, post: 'Post') -> bool:
        """Indicates if the owner of the profile likes a post"""
        return self.user in post.liked.all()

    def __str__(self) -> str:
        return self.user.username


class PostManager(models.Manager):
    def get_by_natural_key(self, post_ref: str) -> 'Post':
        return self.get(post_ref=post_ref)


class Post(models.Model):
    """
    This Model represent a Post. It's considered that a Post only contains one image.
    """
    post_ref = models.CharField(max_length=100, blank=True, unique=True, default=uuid.uuid4, db_index=True)
    author = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE, db_index=True)
    caption = models.CharField(max_length=20)
    created = models.DateTimeField(auto_now=True, db_index=True)
    liked = models.ManyToManyField(User, blank=True, related_name='likers')
    image = models.ImageField()

    index_together = ['created', 'liked']

    objects = PostManager()

    @property
    def liked_number(self) -> int:
        """Number of users that like this Post"""
        return self.liked.count()

    def __str__(self) -> str:
        return f'{self.author}: {self.post_ref}'


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """With this signal we ensure that any new user has a REST token"""
    if created:
        Token.objects.create(user=instance)
        #Profile.objects.get_or_create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
@disable_for_loaddata
def create_profile(sender, instance=None, created=False, **kwargs):
    """With this signal we ensure that any new user has a Profile"""
    if created:
        Profile.objects.get_or_create(user=instance)


@receiver(m2m_changed, sender=Profile.following.through)
def followers_changed(sender, **kwargs):
    """This signal avoid that an User follows himself.

    :raise: FollowException if User try to like himself
    """
    if kwargs['action'] == 'pre_add':
        user = kwargs['instance']
        pk_set = kwargs['pk_set']
        if user.pk in pk_set:
            raise FollowException('User can not follow himself')


@receiver(m2m_changed, sender=Post.liked.through)
def liked_changed(sender, **kwargs):
    """This signal avoid that an User can like his own posts

    :raise: LikeException if User is owner of the Post
    """
    if kwargs['action'] == 'pre_add':
        post = kwargs['instance']
        pk_set = kwargs['pk_set']
        if post.author_id in pk_set:
            raise LikeException('User can not like his own post')
