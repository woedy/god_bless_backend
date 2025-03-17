from django.urls import path

from phone_generator.api.views import (
    clear_numbers_view,
    delete_all_view,
    delete_numbers_view,
    download_csv_view,
    generate_numbers_view,
    get_all_numbers_view,
    get_valid_numbers,
    total_wipe_view,
    validate_numbers_view,
)
from projects.views import add_project_view, archive_project, delete_project, edit_project_view, get_all_archived_projects_view, get_all_projects_view, unarchive_project


app_name = "projects"

urlpatterns = [
    path("add-new-project/", add_project_view, name="add_project_view"),
    path("get-all-projects/", get_all_projects_view, name="get_all_projects_view"),
    path("edit-project/", edit_project_view, name="edit_project_view"),


    path("archive-project/", archive_project, name="archive_project"),
    path("unarchive-project/", unarchive_project, name="unarchive_project"),
    path(
        "get-all-archived-project/",
        get_all_archived_projects_view,
        name="get_all_archived_project_view",
    ),
    path("delete-project/", delete_project, name="delete_project"),
]
