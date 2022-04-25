from unittest import TestCase
import pytest
from django.test import Client
from django.urls import reverse

from posts.models import User, Post


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
        response = self.client.post(
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


class TestingErrors(TestCase):
    def setUp(self):
        self.client = Client()

    def test_page_none_returns_404(self):
        response = self.client.get("this_path_does_not_exist")
        self.assertEqual(response.status_code, 404)