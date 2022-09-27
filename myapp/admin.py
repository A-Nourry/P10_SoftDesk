from django.contrib import admin
from .models import Projects, Contributors, Issues, Comments


class ProjectsAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "description", "type", "author_user_id")


class ContributorsAdmin(admin.ModelAdmin):
    list_display = ("id", "user_id", "project_id", "permission", "role")


class IssuesAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "description",
        "tag",
        "priority",
        "project_id",
        "status",
        "author_user_id",
        "assignee_user_id",
        "created_time",
    )


class CommentsAdmin(admin.ModelAdmin):
    list_display = ("id", "description", "author_user_id", "issue_id", "created_time")


admin.site.register(Projects, ProjectsAdmin)
admin.site.register(Contributors, ContributorsAdmin)
admin.site.register(Issues, IssuesAdmin)
admin.site.register(Comments, CommentsAdmin)
