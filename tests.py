from django.test import TestCase
import pytest
from django.test import Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile, TemporaryUploadedFile
from posts.models import User, Post, Group, Comment
from users.models import Follow


@pytest.mark.django_db(transaction=True)
class TestScenario(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = "yaloh"
        self.password = "loshik123"
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password
        )

    def test_authed_user_has_profile(self):
        response = self.client.get(f'/{self.username}/')
        self.assertEqual(response.status_code, 200)

    def test_non_authed_user_can_not_post(self):
        self.client.logout()
        response = self.client.post(
            reverse("new_post"),
        )
        self.assertEquals(response.status_code, 302)

    def test_authed_user_can_post(self):
        self.client.login(username="yaloh", password="loshik123")
        response = self.client.post(
            reverse("new_post"),
        )
        self.assertEquals(response.status_code, 200)

    def test_new_post_appears_three_places(self):
        self.client.login(username="yaloh", password="loshik123")
        text = "я лох я лох"
        self.client.post(
            reverse("new_post"),
            {"text": text}
        )
        created_post = Post.objects.filter(text=text, author=self.user.id).first()
        self.assertTrue(created_post)
        self.assert_post_appears_three_places(created_post)

    def assert_post_appears_three_places(self, created_post):
        # на странице поста
        response = self.client.get(
            reverse("post", args=(self.user.username, created_post.id)),
        )
        self.assertEqual(response.status_code, 200)

        # на главной странице index
        response = self.client.get(
            reverse("index"),
        )
        html = response.content.decode()
        assert created_post.text in html

        # на странице пользователя
        response = self.client.get(
            reverse("profile", args=(self.user.username,))
        )
        html = response.content.decode()
        assert created_post.text in html

    def test__post_edit__updates_three_places(self):
        self.username="yaloh"
        self.client.login(username=self.username, password="loshik123")
        text = "я не лох я не лох"
        new_text = "лох ли я"
        self.client.post(
            reverse("new_post"),
            {"text": text}
        )
        created_post = Post.objects.filter(text=text, author=self.user.id).first()

        response = self.client.post(
            reverse("post_edit", args=(self.user.username, created_post.id)),
            {"text": new_text}
        )
        self.assertIn(response.status_code, (301, 302))
        updated_post = Post.objects.filter(text=new_text).first()
        self.assertEqual(created_post.id, updated_post.id)
        self.assert_post_appears_three_places(updated_post)


class TestingErrorPages(TestCase):
    def setUp(self):
        self.client = Client()

    def test_page_none_returns_404(self):
        response = self.client.get("this_path_does_not_exist")
        self.assertEqual(response.status_code, 404)


@pytest.mark.django_db(transaction=True)
class TestingImageImport(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="yaloh",
            password="loshik123"
        )
        self.group = Group.objects.create(slug="test_group")

    def test_img_exists(self):
        self.client.login(username="yaloh", password="loshik123")
        with open('media/posts/Untitled.png', 'rb') as img:
            self.client.post(
                reverse('new_post'),
                data={
                    'author': self.user,
                    'text': 'text with image',
                    'image': img,
                    'group': self.group.id
                }
            )

        post = Post.objects.first()
        self.assertEqual(Post.objects.count(), 1)

        urls = [
            reverse('index'),
            reverse('post', kwargs={'username': post.author,
                                    'post_id': post.id}),
            reverse('profile', kwargs={'username': post.author}),
            reverse('group', kwargs={'slug': self.group.slug})
        ]

        for url in urls:
            response = self.client.get(url)
            self.assertContains(response, '<img')

    def test__unable_to_post_invalid_format(self):
        with open('media/posts/Untitled.txt', 'rb') as img:
            self.client.post(
                reverse('new_post'),
                data={
                    'author': self.user,
                    'text': 'text with image',
                    'image': img,
                    'group': self.group.id
                },
                follow=True
            )
        self.assertEqual(Post.objects.count(), 0)


@pytest.mark.django_db(transaction=True)
class TestingCache(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="yaloh",
            password="loshik123"
        )

    def test_cache_index(self):
        self.client.login(username="yaloh", password="loshik123")
        self.client.post(
            reverse("new_post"),
            {"text": "test_text 1"}
        )
        response = self.client.get(reverse('index'))
        self.assertContains(response, "test_text 1")

        self.client.post(
            reverse("new_post"),
            {"text": "test_text 2"}
        )
        response2 = self.client.get(reverse('index'))
        self.assertNotContains(response2, 'test_text 2')


@pytest.mark.django_db(transaction=True)
class TestingFollowing(TestCase):
    def setUp(self):
        self.client = Client()
        self.client2 = Client()
        self.client3 = Client()
        self.user = User.objects.create_user(
            username="yaloh",
            password="loshik123"
        )
        self.user2 = User.objects.create_user(
            username="yaneloh",
            password="neloshik123"
        )
        self.user3 = User.objects.create_user(
            username="loh",
            password="loshped123"
        )

    def test__authed_user_follows__unfollows_others(self):
        self.client.login(username="yaloh", password="loshik123")

        response = self.client.get(reverse("profile_follow", args=(self.user2.username,)))
        self.assertIn(response.status_code, (301, 302))
        before = Follow.objects.all().count()
        self.assertEquals(before, 1)

        response = self.client.get(reverse("profile_unfollow", args=(self.user2.username,)))
        self.assertIn(response.status_code, (301, 302))
        after = Follow.objects.all().count()
        self.assertEquals(after, 0)


    def test__new_post_appears_for_followers__not_for_others(self):
        self.client.login(username="yaloh", password="loshik123")
        self.client3.login(username="loh", password="loshped123")
        self.client.get(reverse("profile_follow", args=(self.user3.username,)))

        self.client3.post(
            reverse("new_post"),
            {"text": "я лох"}
        )
        created_post = Post.objects.filter(text="я лох", author=self.user3.id).first()

        response = self.client.get(reverse("follow_index"))
        html = response.content.decode()
        assert created_post.text in html

        self.client2.login(username="yaneloh", password="neloshik123")
        response = self.client2.get(reverse("follow_index"))
        html = response.content.decode()
        assert created_post.text not in html


