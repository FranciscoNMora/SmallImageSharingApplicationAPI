from PostsApp.models import FollowException, LikeException
from PostsApp.tests.base_test import BaseTest


class UserTests(BaseTest):
    def test_following_number(self):
        self.assertEqual(self.user1.profile.following_number, 1)
        self.assertEqual(self.user2.profile.following_number, 2)
        self.assertEqual(self.user3.profile.following_number, 0)

    def test_followers_number(self):
        self.assertEqual(self.user1.profile.followers_number, 1)
        self.assertEqual(self.user2.profile.followers_number, 0)
        self.assertEqual(self.user3.profile.followers_number, 2)

    def test_follow_user(self):
        self.user3.profile.follow_user(self.user1)
        self.assertEqual(self.user3.profile.following_number, 1)
        self.assertEqual(self.user1.profile.followers_number, 2)
        self.assertIn(self.user1, self.user3.profile.following.all())

    def test_follow_user_itself(self):
        with self.assertRaises(FollowException):
            self.user1.profile.follow_user(self.user1)

    def test_follow_followed_user(self):
        self.assertIn(self.user3, self.user1.profile.following.all())
        self.user1.profile.follow_user(self.user3)
        self.assertEqual(self.user1.profile.following_number, 1)
        self.assertEqual(self.user3.profile.followers_number, 2)

    def test_unfollow_user(self):
        self.user1.profile.unfollow_user(self.user3)
        self.assertEqual(self.user1.profile.following_number, 0)
        self.assertEqual(self.user3.profile.followers_number, 1)

    def test_unfollow_not_followed_user(self):
        self.assertEqual(self.user3.profile.following_number, 0)
        self.assertEqual(self.user1.profile.followers_number, 1)
        self.user3.profile.unfollow_user(self.user1)
        self.assertEqual(self.user3.profile.following_number, 0)
        self.assertEqual(self.user1.profile.followers_number, 1)

    def test_follows(self):
        self.assertTrue(self.user1.profile.follows(self.user3))
        self.assertTrue(self.user2.profile.follows(self.user1))
        self.assertTrue(self.user2.profile.follows(self.user3))
        self.assertFalse(self.user1.profile.follows(self.user2))
        self.assertFalse(self.user3.profile.follows(self.user1))
        self.assertFalse(self.user3.profile.follows(self.user2))

    def test_like_post(self):
        self.user2.profile.like_post(self.post3)
        self.assertIn(self.user2, self.post3.liked.all())

    def test_like_own_post(self):
        with self.assertRaises(LikeException):
            self.user1.profile.like_post(self.post3)

    def test_unlike_post(self):
        self.assertIn(self.user2, self.post1.liked.all())
        self.user2.profile.unlike_post(self.post1)
        self.assertNotIn(self.user2, self.post1.liked.all())

    def test_likes(self):
        self.assertTrue(self.user2.profile.likes(self.post1))
        self.assertTrue(self.user2.profile.likes(self.post2))
        self.assertTrue(self.user3.profile.likes(self.post2))
        self.assertFalse(self.user2.profile.likes(self.post3))
        self.assertFalse(self.user3.profile.likes(self.post1))
        self.assertFalse(self.user3.profile.likes(self.post3))


class PostTests(BaseTest):
    def test_liked_number(self):
        self.assertEqual(self.post1.liked_number, 1)
        self.assertEqual(self.post2.liked_number, 2)
        self.assertEqual(self.post3.liked_number, 0)


