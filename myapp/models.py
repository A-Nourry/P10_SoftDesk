from django.db import models
from django.conf import settings


class Projects(models.Model):
    title = models.CharField(max_length=128, verbose_name="titre")
    description = models.CharField(max_length=1000, verbose_name="description")
    type = models.CharField(max_length=128, verbose_name="type")
    author_user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )


class Contributors(models.Model):
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    project_id = models.ForeignKey(Projects, on_delete=models.CASCADE)
    permission = models.Choices
    role = models.CharField(max_length=128, verbose_name="rôle")


class Issues(models.Model):
    title = models.CharField(max_length=128, verbose_name="titre")
    description = models.CharField(max_length=1000, verbose_name="description")
    tag = models.CharField(max_length=128, verbose_name="balise")
    priority = models.CharField(max_length=128, verbose_name="priorité")
    project_id = models.ForeignKey(Projects, on_delete=models.CASCADE)
    status = models.CharField(max_length=128, verbose_name="status")
    author_user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    assignee_user_id = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assignee_user_id",
    )
    created_time = models.DateTimeField(auto_now_add=True)


class Comments(models.Model):
    description = models.CharField(max_length=1000, verbose_name="description")
    author_user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    issue_id = models.ForeignKey(Issues, on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True)
