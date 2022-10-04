from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.db.models import Q

from .models import Projects, Contributors, Issues, Comments
from .serializers import (
    ProjectsSerializer,
    ContributorsSerializer,
    IssuesSerializer,
    CommentsSerializer,
)

User = get_user_model()


class MultipleSerializerMixin:

    detail_serializer_class = None

    def get_serializer_class(self):
        if self.action == "retrieve" and self.detail_serializer_class is not None:
            return self.detail_serializer_class
        return super().get_serializer_class()


class ProjectView(MultipleSerializerMixin, APIView):

    permission_classes = [IsAuthenticated]

    serializer_class = ProjectsSerializer

    def get(self, request, *args, **kwargs):
        contributors = Contributors.objects.filter(user_id=request.user.id)
        contributors_project_ids = []

        for contributor in contributors:
            contributors_project_ids.append(contributor.project_id.id)

        projects = Projects.objects.filter(
            Q(author_user_id=request.user.id) | Q(id__in=contributors_project_ids)
        )

        serializer = self.serializer_class(projects, many=True)

        return Response(serializer.data)

    def post(self, request: Request):
        data = request.data

        serializer = self.serializer_class(data=data)

        user = User.objects.get(id=request.user.id)

        if serializer.is_valid():
            serializer.save(author_user_id=user)

            response = {
                "message": "Projet créé avec succès !",
                "data": serializer.data,
            }

            return Response(data=response, status=status.HTTP_201_CREATED)

        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DetailProjectView(MultipleSerializerMixin, APIView):

    permission_classes = [IsAuthenticated]

    serializer_class = ProjectsSerializer

    def get(self, request, project_id, *args, **kwargs):
        contributors = Contributors.objects.filter(project_id=project_id)
        contributors_user_ids = []

        for contributor in contributors:
            contributors_user_ids.append(contributor.user_id.id)

        projects = Projects.objects.get(id=project_id)

        current_user = User.objects.get(id=request.user.id)

        if (
            current_user.id not in contributors_user_ids
            and projects.author_user_id != current_user
        ):
            response = {"message": "Vous n'avez pas accès à ce projet !"}

            return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

        else:
            serializer = self.serializer_class(projects, many=False)
            return Response(serializer.data)

    def put(self, request, project_id):
        data = request.data

        project = Projects.objects.get(id=project_id)

        current_user = User.objects.get(id=request.user.id)

        serializer = self.serializer_class(project, data=data)

        if serializer.is_valid() and project.author_user_id == current_user:
            serializer.save()

            response = {
                "message": "Projet modifié avec succès !",
                "data": serializer.data,
            }

            return Response(data=response, status=status.HTTP_201_CREATED)

        else:
            response = {
                "message": "Vous n'êtes pas l'auteur de ce projet : action non autorisé !",
            }

            return Response(data=response)

    def delete(self, request, project_id):

        project = Projects.objects.get(id=project_id)

        current_user = User.objects.get(id=request.user.id)

        if project.author_user_id == current_user:
            project.delete()

            response = {
                "message": "Projet supprimé avec succès !",
            }

            return Response(data=response)
        else:
            response = {
                "message": "Vous n'êtes pas l'auteur de ce projet : action non autorisé !",
            }

            return Response(data=response)


class ContributorsView(MultipleSerializerMixin, APIView):

    permission_classes = [IsAuthenticated]

    serializer_class = ContributorsSerializer

    def get(self, request, project_id, *args, **kwargs):

        contributors = Contributors.objects.filter(project_id=project_id)

        serializer = self.serializer_class(contributors, many=True)

        return Response(serializer.data)

    def post(self, request, project_id):
        data = request.data

        serializer = self.serializer_class(data=data)

        project = Projects.objects.get(id=project_id)
        author = project.author_user_id
        current_user = User.objects.get(id=request.user.id)

        contributors = Contributors.objects.filter(
            project_id=project, user_id=data["user_id"]
        )

        if (
            serializer.is_valid() and len(contributors) < 1 and author == current_user
        ):  # verify if contributors doesn't already exist
            serializer.save(project_id=project)

            response = {
                "message": "Contributeur ajouté avec succès !",
                "data": serializer.data,
            }

            return Response(data=response, status=status.HTTP_201_CREATED)
        else:
            response = {
                "message": "Ce contributeur a déjà été ajouté ou vous n'êtes pas l'auteur de ce projet !",
            }

            return Response(data=response)


class UserContributorsView(MultipleSerializerMixin, APIView):

    permission_classes = [IsAuthenticated]

    serializer_class = ContributorsSerializer

    def delete(self, request, project_id, user_id):

        project = Projects.objects.get(id=project_id)

        user = User.objects.get(id=user_id)

        current_user = User.objects.get(id=request.user.id)

        contributor = Contributors.objects.get(project_id=project, user_id=user)

        if project.author_user_id == current_user:
            contributor.delete()

            response = {
                "message": "contributeur supprimé du projet avec succès !",
            }

            return Response(data=response)
        else:
            response = {
                "message": "Vous n'êtes pas l'auteur de ce projet : action non autorisé !",
            }

            return Response(data=response)


class ProjectIssueView(MultipleSerializerMixin, APIView):

    permission_classes = [IsAuthenticated]

    serializer_class = IssuesSerializer

    def get(self, request, project_id, *args, **kwargs):
        contributors = Contributors.objects.filter(project_id=project_id)
        contributors_user_ids = []

        for contributor in contributors:
            contributors_user_ids.append(contributor.user_id.id)

        projects = Projects.objects.get(id=project_id)

        current_user = User.objects.get(id=request.user.id)

        issue = Issues.objects.filter(project_id=projects.id)
        print(issue)

        if (
            current_user.id not in contributors_user_ids
            and projects.author_user_id != current_user
        ):
            response = {"message": "Vous n'avez pas accès à ce projet !"}

            return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

        else:
            serializer = self.serializer_class(issue, many=True)
            return Response(serializer.data)

    def post(self, request, project_id):
        data = request.data

        contributors = Contributors.objects.filter(project_id=project_id)
        contributors_user_ids = []

        for contributor in contributors:
            contributors_user_ids.append(contributor.user_id.id)

        current_user = User.objects.get(id=request.user.id)

        projects = Projects.objects.get(id=project_id)

        serializer = self.serializer_class(data=data)

        project = Projects.objects.get(id=project_id)

        if (
            current_user.id not in contributors_user_ids
            and projects.author_user_id != current_user
        ):
            response = {
                "message": "Vous ne participez pas à ce projet : Accès non autorisé !"
            }

            return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

        else:
            if serializer.is_valid():
                serializer.save(project_id=project, author_user_id=current_user)

                response = {
                    "message": "Problème créé avec succès !",
                    "data": serializer.data,
                }

                return Response(data=response, status=status.HTTP_201_CREATED)

            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class IssueView(MultipleSerializerMixin, APIView):

    permission_classes = [IsAuthenticated]

    serializer_class = IssuesSerializer

    def put(self, request, project_id, issue_id):
        data = request.data

        issue = Issues.objects.get(id=issue_id, project_id=project_id)

        current_user = User.objects.get(id=request.user.id)

        serializer = self.serializer_class(issue, data=data)

        if serializer.is_valid() and issue.author_user_id == current_user:
            serializer.save()

            response = {
                "message": "Problème modifié avec succès !",
                "data": serializer.data,
            }

            return Response(data=response, status=status.HTTP_201_CREATED)

        else:
            response = {
                "message": "Vous n'êtes pas l'auteur de ce problème : action non autorisé !",
            }

            return Response(data=response)

    def delete(self, request, project_id, issue_id):

        issue = Issues.objects.get(id=issue_id, project_id=project_id)

        current_user = User.objects.get(id=request.user.id)

        if issue.author_user_id == current_user:
            issue.delete()

            response = {
                "message": "Problème supprimé avec succès !",
            }

            return Response(data=response, status=status.HTTP_201_CREATED)
        else:
            response = {
                "message": "Vous n'êtes pas l'auteur de ce problème: action non autorisé !",
            }

        return Response(data=response)


class IssueCommentView(MultipleSerializerMixin, APIView):

    permission_classes = [IsAuthenticated]

    serializer_class = CommentsSerializer

    def get(self, request, project_id, issue_id, *args, **kwargs):
        contributors = Contributors.objects.filter(project_id=project_id)
        contributors_user_ids = []

        for contributor in contributors:
            contributors_user_ids.append(contributor.user_id.id)

        projects = Projects.objects.get(id=project_id)

        current_user = User.objects.get(id=request.user.id)

        issue = Issues.objects.get(id=issue_id, project_id=project_id)

        comment = Comments.objects.filter(issue_id=issue)

        if (
            current_user.id not in contributors_user_ids
            and projects.author_user_id != current_user
        ):
            response = {"message": "Vous n'avez pas accès à ce projet !"}

            return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

        else:

            serializer = self.serializer_class(comment, many=True)

            return Response(serializer.data)

    def post(self, request, project_id, issue_id):
        contributors = Contributors.objects.filter(project_id=project_id)
        contributors_user_ids = []

        for contributor in contributors:
            contributors_user_ids.append(contributor.user_id.id)

        projects = Projects.objects.get(id=project_id)

        current_user = User.objects.get(id=request.user.id)

        issue = Issues.objects.get(id=issue_id, project_id=project_id)

        data = request.data

        serializer = self.serializer_class(data=data)

        issue = Issues.objects.get(id=issue_id, project_id=project_id)

        if (
            current_user.id not in contributors_user_ids
            and projects.author_user_id != current_user
        ):
            response = {
                "message": "Vous ne participez pas à ce projet : Accès non autorisé !"
            }

            return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

        else:
            if serializer.is_valid():
                serializer.save(issue_id=issue, author_user_id=current_user)

                response = {
                    "message": "Commentaire créé avec succès !",
                    "data": serializer.data,
                }

                return Response(data=response, status=status.HTTP_201_CREATED)

            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentView(MultipleSerializerMixin, APIView):

    permission_classes = [IsAuthenticated]

    serializer_class = CommentsSerializer

    def get(self, request, project_id, issue_id, comment_id, *args, **kwargs):
        contributors = Contributors.objects.filter(project_id=project_id)
        contributors_user_ids = []

        for contributor in contributors:
            contributors_user_ids.append(contributor.user_id.id)

        projects = Projects.objects.get(id=project_id)

        current_user = User.objects.get(id=request.user.id)

        issue = Issues.objects.get(id=issue_id, project_id=project_id)

        comment = Comments.objects.get(id=comment_id, issue_id=issue)

        if (
            current_user.id not in contributors_user_ids
            and projects.author_user_id != current_user
        ):
            response = {
                "message": "Vous ne participez pas à ce projet : Accès refusé !"
            }

            return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

        else:

            serializer = self.serializer_class(comment, many=False)

            return Response(serializer.data)

    def put(self, request, project_id, issue_id, comment_id):
        data = request.data

        issue = Issues.objects.get(id=issue_id, project_id=project_id)

        comment = Comments.objects.get(id=comment_id, issue_id=issue)

        current_user = User.objects.get(id=request.user.id)

        serializer = self.serializer_class(comment, data=data)

        if serializer.is_valid() and comment.author_user_id == current_user:
            serializer.save()

            response = {
                "message": "commentaire modifié avec succès !",
                "data": serializer.data,
            }

            return Response(data=response, status=status.HTTP_201_CREATED)

        else:
            response = {
                "message": "Vous n'êtes pas l'auteur de ce commentaire : action non autorisé !",
            }

            return Response(data=response)

    def delete(self, request, project_id, issue_id, comment_id):

        issue = Issues.objects.get(id=issue_id, project_id=project_id)

        comment = Comments.objects.get(id=comment_id, issue_id=issue)

        current_user = User.objects.get(id=request.user.id)

        if comment.author_user_id == current_user:
            comment.delete()

            response = {
                "message": "Commentaire supprimé avec succès !",
            }

            return Response(data=response)
        else:
            response = {
                "message": "Vous n'êtes pas l'auteur de ce commentaire: action non autorisé !",
            }

            return Response(data=response)
