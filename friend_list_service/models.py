from django.db import models
import uuid


class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=20)
    friend_list = models.ManyToManyField("self", blank=True)


class Requests(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    from_user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='outcoming_requests')
    to_user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='incoming_requests')
