from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model

from .models import Projects
from .serializers import ProjectsSerializer

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

        projects = Projects.objects.filter(author_user_id=request.user.id)

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

        projects = Projects.objects.filter(id=project_id)

        serializer = self.serializer_class(projects, many=True)

        return Response(serializer.data)

    def put(self, request, project_id):
        data = request.data

        project = Projects.objects.get(id=project_id)

        serializer = self.serializer_class(project, data=data)

        if serializer.is_valid():
            serializer.save()

            response = {
                "message": "Projet modifié avec succès !",
                "data": serializer.data,
            }

            return Response(data=response, status=status.HTTP_201_CREATED)

        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, project_id):

        project = Projects.objects.get(id=project_id)

        current_user = User.objects.get(id=request.user.id)

        if project.author_user_id == current_user:
            project.delete()

            response = {
                "message": "Projet supprimé avec succès !",
            }
        else:
            response = {
                "message": "Vous n'êtes pas l'auteur de ce projet : action non autorisé !",
            }

        return Response(data=response, status=status.HTTP_201_CREATED)
