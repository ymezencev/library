from django.contrib.auth.models import User
from django.db import models


class Book(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    author_name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                              related_name='my_books')

    readers = models.ManyToManyField(User, through='UserBookRelation',
                                     related_name='books')
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=None,
                                 null=True)

    def __str__(self):
        return f'Id {self.id}: {self.name}'

class UserBookRelation(models.Model):
    RATE_CHOICES = (
        (1, 'Ok'),
        (2, 'Fine'),
        (3, 'Good'),
        (4, 'Amazing'),
        (5, 'Incredible'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    like = models.BooleanField(default=False)
    in_bookmarks = models.BooleanField(default=False)
    rate = models.PositiveSmallIntegerField(choices=RATE_CHOICES, null=True)

    def __str__(self):
        return f'User {self.user.username}, Book {self.book.name}, (rate {self.rate}*)'

    def save(self, *args, **kwargs):
        from store.services.book import set_rating
        is_creating = not self.pk
        old_rating = None
        if not is_creating:
            old_rating = UserBookRelation.objects.get(id=self.id).rate
        super().save(*args, **kwargs)

        new_rating = self.rate
        if old_rating != new_rating or is_creating:
            set_rating(self.book)
            print(f'{self.book.name}: {old_rating}->>{new_rating} [{self.book.rating}]')
