from django.db import models
from django.contrib.auth.models import User

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]

CATEGORY_CHOICES = [
    ("photography", "Photography"),
    ("travel", "Travel"),
    ("food", "Food & Drink"),
    ("fashion", "Fashion"),
    ("art", "Art & Design"),
    ("nature", "Nature"),
    ("architecture", "Architecture"),
    ("lifestyle", "Lifestyle"),
    ("sport", "Sport & Fitness"),
    ("technology", "Technology"),
    ("music", "Music"),
    ("other", "Other"),
]

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    image = models.ImageField(upload_to='posts/%Y/%m/')
    description = models.TextField(max_length=2000, blank=True)
    location = models.CharField(max_length=200, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, blank=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.author.username} - {self.created_at.strftime("%Y-%m-%d")}'

    def get_likes_count(self):
        return self.likes.count()

    def get_comments_count(self):
        return self.comments.count()

    def is_liked_by(self, user):
        return self.likes.filter(user=user).exists()

    def is_bookmarked_by(self, user):
        return self.bookmarks.filter(user=user).exists()


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self):
        return f'{self.user.username} likes post {self.post.id}'


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.user.username} on post {self.post.id}'


class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='bookmarks')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self):
        return f'{self.user.username} bookmarked post {self.post.id}'
