from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField
from .models import Projects, Contributors, Issues, Comments


class ProjectsSerializer(ModelSerializer):

    author_user_id = PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Projects
        fields = ["id", "title", "description", "type", "author_user_id"]


class ContributorsSerializer(ModelSerializer):
    project_id = PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Contributors
        fields = ["id", "user_id", "project_id", "permission", "role"]


class IssuesSerializer(ModelSerializer):
    author_user_id = PrimaryKeyRelatedField(read_only=True)
    project_id = PrimaryKeyRelatedField(read_only=True)

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


class CommentsSerializer(ModelSerializer):
    class Meta:
        model = Comments
        fields = ["id", "description", "author_user_id", "issue_id", "created_time"]
