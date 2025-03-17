from django.shortcuts import render
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework import status

from projects.models import Project


from django.contrib.auth import get_user_model
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication

from projects.serializers import AllProjectsSerializer


User = get_user_model()


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def add_project_view(request):
    payload = {}
    data = {}
    errors = {}

    if request.method == "POST":
        project_name = request.data.get("project_name", "")
        description = request.data.get("description", "")
        user_id = request.data.get("user_id", "")

        # Validation for required fields
        if not project_name:
            errors["project_name"] = ["Project Name is required."]
      
        if not user_id:
            errors["user_id"] = ["User ID is required."]

        try:
            user = User.objects.get(user_id=user_id)
        except:
            errors["user_id"] = ["User does not exist."]

        # Check if the name is already taken
        if Project.objects.filter(user=user, project_name=project_name).exists():
            errors["project_name"] = ["A Project with this name already exists."]

        if errors:
            payload["message"] = "Errors"
            payload["errors"] = errors
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)

        # Create the new food category
        new_project = Project.objects.create(
            user=user,
            project_name=project_name,
            description=description,
        )

        # Prepare response data
        data["id"] = new_project.id
        data["project_name"] = new_project.project_name
        data["description"] = new_project.description

        payload["message"] = "Project added successfully"
        payload["data"] = data

    return Response(payload, status=status.HTTP_201_CREATED)


@api_view(
    [
        "GET",
    ]
)
@permission_classes(
    [
        IsAuthenticated,
    ]
)
@authentication_classes(
    [
        TokenAuthentication,
    ]
)
def get_all_projects_view(request):
    payload = {}
    data = {}
    errors = {}

    search_query = request.query_params.get("search", "")
    user_id = request.query_params.get("user_id", "")
    page_number = request.query_params.get("page", 1)
    page_size = 10

    if not user_id:
        errors["user_id"] = ["User ID is required."]

    try:
        user = User.objects.get(user_id=user_id)
    except:
        errors["user_id"] = ["User does not exist."]
    if errors:
        payload["message"] = "Errors"
        payload["errors"] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    all_projects = Project.objects.all().filter(is_archived=False, user=user)

    if search_query:
        all_projects = all_projects.filter(Q(name__icontains=search_query))

    paginator = Paginator(all_projects, page_size)

    try:
        paginated_projects = paginator.page(page_number)
    except PageNotAnInteger:
        paginated_projects = paginator.page(1)
    except EmptyPage:
        paginated_projects = paginator.page(paginator.num_pages)

    all_projects_serializer = AllProjectsSerializer(paginated_projects, many=True)

    data["projects"] = all_projects_serializer.data
    data["pagination"] = {
        "page_number": paginated_projects.number,
        "total_pages": paginator.num_pages,
        "next": (
            paginated_projects.next_page_number()
            if paginated_projects.has_next()
            else None
        ),
        "previous": (
            paginated_projects.previous_page_number()
            if paginated_projects.has_previous()
            else None
        ),
    }

    payload["message"] = "Successful"
    payload["data"] = data

    return Response(payload, status=status.HTTP_200_OK)


@api_view(
    [
        "POST",
    ]
)
@permission_classes(
    [
        IsAuthenticated,
    ]
)
@authentication_classes(
    [
        TokenAuthentication,
    ]
)
def edit_project_view(request):
    payload = {}
    data = {}
    errors = {}

    if request.method == "POST":
        project_id = request.data.get("project_id", "")
        name = request.data.get("name", "")
        description = request.data.get("description", "")

        if not project_id:
            errors["project_id"] = ["Project ID is required."]
        if not name:
            errors["name"] = ["Name id required"]

        if not description:
            errors["description"] = ["Description is required."]

        try:
            project = Project.objects.get(project_id=project_id)
        except:
            errors["project_id"] = ["Project does not exist."]

        # Check if the name is already taken
        if Project.objects.filter(user=project.user, name=name).exists():
            errors["name"] = ["A Project with this name already exists."]

        if errors:
            payload["message"] = "Errors"
            payload["errors"] = errors
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)

        # Update fields only if provided and not empty
        if name:
            if name != project.name:
                project.name = name
        if description:
            project.description = description

        project.save()

        data["name"] = project.name

        payload["message"] = "Successful"
        payload["data"] = data

    return Response(payload)


@api_view(
    [
        "POST",
    ]
)
@permission_classes(
    [
        IsAuthenticated,
    ]
)
@authentication_classes(
    [
        TokenAuthentication,
    ]
)
def archive_project(request):
    payload = {}
    data = {}
    errors = {}

    if request.method == "POST":
        project_id = request.data.get("project_id", "")

        if not project_id:
            errors["project_id"] = ["Project ID is required."]

        try:
            project = Project.objects.get(project_id=project_id)
        except:
            errors["project_id"] = ["Project does not exist."]

        if errors:
            payload["message"] = "Errors"
            payload["errors"] = errors
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)

        project.is_archived = True
        project.save()

        payload["message"] = "Successful"
        payload["data"] = data

    return Response(payload)


@api_view(
    [
        "POST",
    ]
)
@permission_classes(
    [
        IsAuthenticated,
    ]
)
@authentication_classes(
    [
        TokenAuthentication,
    ]
)
def unarchive_project(request):
    payload = {}
    data = {}
    errors = {}

    if request.method == "POST":
        project_id = request.data.get("project_id", "")

        if not project_id:
            errors["project_id"] = ["Project ID is required."]

        try:
            project = Project.objects.get(project_id=project_id)
        except:
            errors["project_id"] = ["Project does not exist."]

        if errors:
            payload["message"] = "Errors"
            payload["errors"] = errors
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)

        project.is_archived = False
        project.save()

        payload["message"] = "Successful"
        payload["data"] = data

    return Response(payload)


@api_view(
    [
        "POST",
    ]
)
@permission_classes(
    [
        IsAuthenticated,
    ]
)
@authentication_classes(
    [
        TokenAuthentication,
    ]
)
def delete_project(request):
    payload = {}
    data = {}
    errors = {}

    if request.method == "POST":
        project_id = request.data.get("project_id", "")

        if not project_id:
            errors["project_id"] = ["Project ID is required."]

        try:
            project = Project.objects.get(id=project_id)
        except:
            errors["project_id"] = ["Project does not exist."]

        if errors:
            payload["message"] = "Errors"
            payload["errors"] = errors
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)

        project.delete()

        payload["message"] = "Successful"
        payload["data"] = data

    return Response(payload)


@api_view(
    [
        "GET",
    ]
)
@permission_classes(
    [
        IsAuthenticated,
    ]
)
@authentication_classes(
    [
        TokenAuthentication,
    ]
)
def get_all_archived_projects_view(request):
    payload = {}
    data = {}
    errors = {}

    search_query = request.query_params.get("search", "")
    user_id = request.query_params.get("user_id", "")
    page_number = request.query_params.get("page", 1)
    page_size = 10

    if not user_id:
        errors["user_id"] = ["User ID is required."]

    try:
        user = User.objects.get(user_id=user_id)
    except:
        errors["user_id"] = ["User does not exist."]
    if errors:
        payload["message"] = "Errors"
        payload["errors"] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    all_projects = Project.objects.all().filter(is_archived=True, user=user)

    if search_query:
        all_projects = all_projects.filter(Q(name__icontains=search_query))

    paginator = Paginator(all_projects, page_size)

    try:
        paginated_projects = paginator.page(page_number)
    except PageNotAnInteger:
        paginated_projects = paginator.page(1)
    except EmptyPage:
        paginated_projects = paginator.page(paginator.num_pages)

    all_projects_serializer = AllProjectsSerializer(paginated_projects, many=True)

    data["projects"] = all_projects_serializer.data
    data["pagination"] = {
        "page_number": paginated_projects.number,
        "total_pages": paginator.num_pages,
        "next": (
            paginated_projects.next_page_number()
            if paginated_projects.has_next()
            else None
        ),
        "previous": (
            paginated_projects.previous_page_number()
            if paginated_projects.has_previous()
            else None
        ),
    }

    payload["message"] = "Successful"
    payload["data"] = data

    return Response(payload, status=status.HTTP_200_OK)
