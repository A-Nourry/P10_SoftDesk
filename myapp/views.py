from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist

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
    """View for /project/"""

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
    """View for /project/<project_id>"""

    permission_classes = [IsAuthenticated]

    serializer_class = ProjectsSerializer

    def get(self, request, project_id, *args, **kwargs):
        contributors = Contributors.objects.filter(project_id=project_id)
        contributors_user_ids = []

        for contributor in contributors:
            contributors_user_ids.append(contributor.user_id.id)

        try:
            projects = Projects.objects.get(id=project_id)
        except ObjectDoesNotExist as e:
            response = {"message": "Projet non trouvé ! " + str(e)}
            return Response(data=response, status=status.HTTP_404_NOT_FOUND)

        current_user = User.objects.get(id=request.user.id)

        if (
            current_user.id not in contributors_user_ids
            and projects.author_user_id != current_user
        ):
            response = {"message": "Vous n'avez pas accès à ce projet !"}

            return Response(data=response, status=status.HTTP_403_FORBIDDEN)

        else:
            serializer = self.serializer_class(projects, many=False)
            return Response(serializer.data)

    def put(self, request, project_id):
        data = request.data

        try:
            project = Projects.objects.get(id=project_id)
        except ObjectDoesNotExist as e:
            response = {"message": "Projet non trouvé ! " + str(e)}
            return Response(data=response, status=status.HTTP_404_NOT_FOUND)

        current_user = User.objects.get(id=request.user.id)

        serializer = self.serializer_class(project, data=data)

        if serializer.is_valid() and project.author_user_id == current_user:
            serializer.save()

            response = {
                "message": "Projet modifié avec succès !",
                "data": serializer.data,
            }

            return Response(data=response, status=status.HTTP_200_OK)

        else:
            response = {
                "message": "Vous n'êtes pas l'auteur de ce projet : action non autorisé !",
            }

            return Response(data=response, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, project_id):

        try:
            project = Projects.objects.get(id=project_id)
        except ObjectDoesNotExist as e:
            response = {"message": "Projet non trouvé ! " + str(e)}
            return Response(data=response, status=status.HTTP_404_NOT_FOUND)

        current_user = User.objects.get(id=request.user.id)

        if project.author_user_id == current_user:
            project.delete()

            response = {
                "message": "Projet supprimé avec succès !",
            }

            return Response(data=response, status=status.HTTP_200_OK)
        else:
            response = {
                "message": "Vous n'êtes pas l'auteur de ce projet : action non autorisé !",
            }

            return Response(data=response, status=status.HTTP_403_FORBIDDEN)


class ContributorsView(MultipleSerializerMixin, APIView):
    """View for /project/<project_id>/users/"""

    permission_classes = [IsAuthenticated]

    serializer_class = ContributorsSerializer

    def get(self, request, project_id, *args, **kwargs):
        try:
            project = Projects.objects.get(id=project_id)
        except ObjectDoesNotExist as e:
            response = {"message": "Projet non trouvé ! " + str(e)}
            return Response(data=response, status=status.HTTP_404_NOT_FOUND)

        contributors = Contributors.objects.filter(project_id=project)

        serializer = self.serializer_class(contributors, many=True)

        if len(contributors) > 0:
            return Response(serializer.data)

        else:
            response = {
                "message": "Ce projet n'a pas de contributeurs.",
            }

            return Response(data=response, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, project_id):
        data = request.data

        serializer = self.serializer_class(data=data)

        try:
            project = Projects.objects.get(id=project_id)
        except ObjectDoesNotExist as e:
            response = {"message": "Projet non trouvé ! " + str(e)}
            return Response(data=response, status=status.HTTP_404_NOT_FOUND)

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

            return Response(data=response, status=status.HTTP_403_FORBIDDEN)


class UserContributorsView(MultipleSerializerMixin, APIView):
    """View for /project/<project_id>/users/<user_id>"""

    permission_classes = [IsAuthenticated]

    serializer_class = ContributorsSerializer

    def delete(self, request, project_id, user_id):

        try:
            project = Projects.objects.get(id=project_id)
        except ObjectDoesNotExist as e:
            response = {"message": "Projet non trouvé ! " + str(e)}
            return Response(data=response, status=status.HTTP_404_NOT_FOUND)

        try:
            user = User.objects.get(id=user_id)
        except ObjectDoesNotExist as e:
            response = {"message": "Utilisateur non trouvé ! " + str(e)}
            return Response(data=response, status=status.HTTP_404_NOT_FOUND)

        current_user = User.objects.get(id=request.user.id)

        contributor = Contributors.objects.get(project_id=project, user_id=user)

        if project.author_user_id == current_user:
            contributor.delete()

            response = {
                "message": "contributeur supprimé du projet avec succès !",
            }

            return Response(data=response, status=status.HTTP_200_OK)
        else:
            response = {
                "message": "Vous n'êtes pas l'auteur de ce projet : action non autorisé !",
            }

            return Response(data=response, status=status.HTTP_403_FORBIDDEN)


class ProjectIssueView(MultipleSerializerMixin, APIView):
    """View for /project/<project_id>/issues/"""

    permission_classes = [IsAuthenticated]

    serializer_class = IssuesSerializer

    def get(self, request, project_id, *args, **kwargs):
        contributors = Contributors.objects.filter(project_id=project_id)
        contributors_user_ids = []

        for contributor in contributors:
            contributors_user_ids.append(contributor.user_id.id)

        try:
            projects = Projects.objects.get(id=project_id)
        except ObjectDoesNotExist as e:
            response = {"message": "Projet non trouvé ! " + str(e)}
            return Response(data=response, status=status.HTTP_404_NOT_FOUND)

        current_user = User.objects.get(id=request.user.id)

        issue = Issues.objects.filter(project_id=projects.id)
        print(issue)

        if (
            current_user.id not in contributors_user_ids
            and projects.author_user_id != current_user
        ):
            response = {"message": "Vous n'avez pas accès à ce projet !"}

            return Response(data=response, status=status.HTTP_403_FORBIDDEN)

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

        try:
            projects = Projects.objects.get(id=project_id)
        except ObjectDoesNotExist as e:
            response = {"message": "Projet non trouvé ! " + str(e)}
            return Response(data=response, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(data=data)

        project = Projects.objects.get(id=project_id)

        if (
            current_user.id not in contributors_user_ids
            and projects.author_user_id != current_user
        ):
            response = {
                "message": "Vous ne participez pas à ce projet : Accès non autorisé !"
            }

            return Response(data=response, status=status.HTTP_403_FORBIDDEN)

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
    """View for /project/<project_id>/issues/<issue_id>"""

    permission_classes = [IsAuthenticated]

    serializer_class = IssuesSerializer

    def put(self, request, project_id, issue_id):
        data = request.data

        try:
            issue = Issues.objects.get(id=issue_id, project_id=project_id)
            print(issue)
        except ObjectDoesNotExist as e:
            response = {"message": "Projet ou problème non trouvé ! " + str(e)}
            return Response(data=response, status=status.HTTP_404_NOT_FOUND)

        current_user = User.objects.get(id=request.user.id)

        serializer = self.serializer_class(issue, data=data)

        if serializer.is_valid() and issue.author_user_id == current_user:
            serializer.save()

            response = {
                "message": "Problème modifié avec succès !",
                "data": serializer.data,
            }

            return Response(data=response, status=status.HTTP_200_OK)

        else:
            if serializer.is_valid():
                response = {
                    "message": "Vous n'êtes pas l'auteur de ce problème : action non autorisé !",
                }

                return Response(data=response, status=status.HTTP_403_FORBIDDEN)
            else:

                return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, project_id, issue_id):

        try:
            issue = Issues.objects.get(id=issue_id, project_id=project_id)
        except ObjectDoesNotExist as e:
            response = {"message": "Projet ou problème non trouvé ! " + str(e)}
            return Response(data=response, status=status.HTTP_404_NOT_FOUND)

        current_user = User.objects.get(id=request.user.id)

        if issue.author_user_id == current_user:
            issue.delete()

            response = {
                "message": "Problème supprimé avec succès !",
            }

            return Response(data=response, status=status.HTTP_200_OK)
        else:
            response = {
                "message": "Vous n'êtes pas l'auteur de ce problème: action non autorisé !",
            }

        return Response(data=response, status=status.HTTP_403_FORBIDDEN)


class IssueCommentView(MultipleSerializerMixin, APIView):
    """View for /project/<project_id>/issues/<issue_id>/comments/"""

    permission_classes = [IsAuthenticated]

    serializer_class = CommentsSerializer

    def get(self, request, project_id, issue_id, *args, **kwargs):
        contributors = Contributors.objects.filter(project_id=project_id)
        contributors_user_ids = []

        for contributor in contributors:
            contributors_user_ids.append(contributor.user_id.id)

        current_user = User.objects.get(id=request.user.id)

        try:
            projects = Projects.objects.get(id=project_id)
            issue = Issues.objects.get(id=issue_id, project_id=project_id)
        except ObjectDoesNotExist as e:
            response = {"message": "Problème ou projet non trouvé ! : " + str(e)}
            return Response(data=response, status=status.HTTP_404_NOT_FOUND)

        comment = Comments.objects.filter(issue_id=issue)

        if (
            current_user.id not in contributors_user_ids
            and projects.author_user_id != current_user
        ):
            response = {"message": "Vous n'avez pas accès à ce projet !"}

            return Response(data=response, status=status.HTTP_403_FORBIDDEN)

        else:
            if len(comment) > 0:
                serializer = self.serializer_class(comment, many=True)
                return Response(serializer.data)
            else:
                response = {
                    "message": "Il n'a pas encore de commentaire sur ce problème.",
                }

                return Response(data=response, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, project_id, issue_id):
        contributors = Contributors.objects.filter(project_id=project_id)
        contributors_user_ids = []

        for contributor in contributors:
            contributors_user_ids.append(contributor.user_id.id)

        current_user = User.objects.get(id=request.user.id)

        try:
            projects = Projects.objects.get(id=project_id)
        except ObjectDoesNotExist as e:
            response = {"message": "Projet non trouvé ! " + str(e)}
            return Response(data=response, status=status.HTTP_404_NOT_FOUND)

        try:
            issue = Issues.objects.get(id=issue_id, project_id=project_id)
        except ObjectDoesNotExist as e:
            response = {"message": "Problème non trouvé ! " + str(e)}
            return Response(data=response, status=status.HTTP_404_NOT_FOUND)

        data = request.data

        serializer = self.serializer_class(data=data)

        if (
            current_user.id not in contributors_user_ids
            and projects.author_user_id != current_user
        ):
            response = {
                "message": "Vous ne participez pas à ce projet : Accès non autorisé !"
            }

            return Response(data=response, status=status.HTTP_403_FORBIDDEN)

        else:
            if serializer.is_valid():
                serializer.save(issue_id=issue, author_user_id=current_user)

                response = {
                    "message": "Commentaire créé avec succès !",
                    "data": serializer.data,
                }

                return Response(data=response, status=status.HTTP_200_OK)

            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentView(MultipleSerializerMixin, APIView):
    """View for /project/<project_id>/issues/<issue_id>/comments/<comment_id>"""

    permission_classes = [IsAuthenticated]

    serializer_class = CommentsSerializer

    def get(self, request, project_id, issue_id, comment_id, *args, **kwargs):
        contributors = Contributors.objects.filter(project_id=project_id)
        contributors_user_ids = []

        for contributor in contributors:
            contributors_user_ids.append(contributor.user_id.id)

        current_user = User.objects.get(id=request.user.id)

        try:
            projects = Projects.objects.get(id=project_id)
            issue = Issues.objects.get(id=issue_id, project_id=project_id)
            comment = Comments.objects.get(id=comment_id, issue_id=issue)
        except ObjectDoesNotExist as e:
            response = {
                "message": "Projet, problème ou commentaire non trouvé ! : " + str(e)
            }
            return Response(data=response, status=status.HTTP_404_NOT_FOUND)

        if (
            current_user.id not in contributors_user_ids
            and projects.author_user_id != current_user
        ):
            response = {
                "message": "Vous ne participez pas à ce projet : Accès refusé !"
            }

            return Response(data=response, status=status.HTTP_403_FORBIDDEN)

        else:

            serializer = self.serializer_class(comment, many=False)

            return Response(serializer.data)

    def put(self, request, project_id, issue_id, comment_id):
        data = request.data

        current_user = User.objects.get(id=request.user.id)

        try:
            issue = Issues.objects.get(id=issue_id, project_id=project_id)
            comment = Comments.objects.get(id=comment_id, issue_id=issue)
        except ObjectDoesNotExist as e:
            response = {
                "message": "Projet, problème ou commentaire non trouvé ! : " + str(e)
            }
            return Response(data=response, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(comment, data=data)

        if serializer.is_valid() and comment.author_user_id == current_user:
            serializer.save()

            response = {
                "message": "commentaire modifié avec succès !",
                "data": serializer.data,
            }

            return Response(data=response, status=status.HTTP_200_OK)

        else:
            response = {
                "message": "Vous n'êtes pas l'auteur de ce commentaire : action non autorisé !",
            }

            return Response(data=response, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, project_id, issue_id, comment_id):

        try:
            issue = Issues.objects.get(id=issue_id, project_id=project_id)
            comment = Comments.objects.get(id=comment_id, issue_id=issue)
        except ObjectDoesNotExist as e:
            response = {
                "message": "Projet, problème ou commentaire non trouvé ! : " + str(e)
            }
            return Response(data=response, status=status.HTTP_404_NOT_FOUND)

        current_user = User.objects.get(id=request.user.id)

        if comment.author_user_id == current_user:
            comment.delete()

            response = {
                "message": "Commentaire supprimé avec succès !",
            }

            return Response(data=response, status=status.HTTP_200_OK)
        else:
            response = {
                "message": "Vous n'êtes pas l'auteur de ce commentaire: action non autorisé !",
            }

            return Response(data=response, status=status.HTTP_403_FORBIDDEN)
