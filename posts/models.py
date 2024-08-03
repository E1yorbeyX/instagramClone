from django.db import models
from django.contrib.auth import get_user_model
from shared.models import Base
from django.core.validators import FileExtensionValidator, MaxLengthValidator
from django.db.models import UniqueConstraint

User = get_user_model()

class Post(Base):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    image = models.ImageField(upload_to='posts_photos', validators=[FileExtensionValidator(allowed_extensions=['jpg', 'png', 'jpeg'])])
    caption = models.TextField(validators=[MaxLengthValidator(2000)])

    class Meta:
        db_table = 'post'
        verbose_name = 'post'
        verbose_name_plural = 'posts'
    
    def __str__(self):
        return f'{self.author.username}ning {self.caption}'
    
class PostCommet(Base):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='postcommit')
    commet = models.TextField(validators=[MaxLengthValidator(2000)])
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name = 'child',
        null=True,
        blank=True
    )

    def __str__(self):
        return f'{self.author.username} commeted {self.post}'

class PostLike(Base):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='postlike')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'post'],
                name='unique_like_for_post'
            )
        ]

    def __str__(self):
        return f'{self.author.username} liked {self.post}'

class CommetLike(Base):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    commet = models.ForeignKey(PostCommet, on_delete=models.CASCADE, related_name='commitlike')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'commet'],
                name='unique_like_for_commet'
            )
        ]
    def __str__(self):
        return f'{self.author.username} Commed Liked {self.commet}'
