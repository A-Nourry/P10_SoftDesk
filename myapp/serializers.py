from rest_framework.serializers import ModelSerializer
from .models import Projects, Contributors, Issues, Comments


class ProjectsSerializer(ModelSerializer):
    class Meta:
        model = Projects
        fields = ["id", "title", "description", "type", "author_user_id"]


class ContributorsSerializers(ModelSerializer):
    class Meta:
        model = Contributors
        fields = ["id", "user_id", "project_id", "permission", "role"]


class IssuesSerializers(ModelSerializer):
    class Meta:
        model = Issues
        fields = [
            "id",
            "title",
            "description",
            "tag",
            "priority",
            "project_id",
            "status",
            "author_user_id",
            "assignee_user_id",
            "created_time",
        ]


class CommentsSerializers(ModelSerializer):
    class Meta:
        model = Comments
        fields = ["id", "description", "author_user_id", "issue_id", "created_time"]
