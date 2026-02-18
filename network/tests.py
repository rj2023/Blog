from django.test import TestCase, Client
from django.urls import reverse
from .models import User, Post, PostInteraction, Comment

class NetworkTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password')
        self.client = Client()

    def test_index_page(self):
        """Test that index page loads successfully."""
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_login(self):
        """Test user login."""
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'password'})
        self.assertEqual(response.status_code, 302)  # Should redirect to index
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_create_post(self):
        """Test creating a post."""
        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('create_post_submit'), {
            'title': 'Test Post',
            'content': 'This is a test post content.',
            'tags': '#test'
        })
        self.assertEqual(response.status_code, 302)  # Should redirect to index
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.first()
        self.assertEqual(post.title, 'Test Post')
        self.assertEqual(post.tags.count(), 1)

    def test_like_post(self):
        """Test liking a post."""
        self.client.login(username='testuser', password='password')
        post = Post.objects.create(author=self.user, title='Post to Like', content='Content')

        response = self.client.post(reverse('like_unlike_post'), {'post_id': post.id})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['liked'])
        self.assertEqual(post.get_like_count(), 1)

        # Unlike
        response = self.client.post(reverse('like_unlike_post'), {'post_id': post.id})
        self.assertFalse(response.json()['liked'])
        self.assertEqual(post.get_like_count(), 0)

    def test_comment_post(self):
        """Test commenting on a post."""
        self.client.login(username='testuser', password='password')
        post = Post.objects.create(author=self.user, title='Post to Comment', content='Content')

        response = self.client.post(reverse('add_comment'), {
            'post_id': post.id,
            'comment': 'Nice post!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertEqual(Comment.objects.count(), 1)
        comment = Comment.objects.first()
        self.assertEqual(comment.content, 'Nice post!')

    def test_profile_page(self):
        """Test profile page loads."""
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('profile', args=[self.user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.username)
