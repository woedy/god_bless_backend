from django.urls import path

from smtps.views import add_smtp_view, delete_smtp, get_smtps_view



app_name = 'smtps'

urlpatterns = [
    path('add-smtp/', add_smtp_view, name="add_smtp_view"),
    path('get-smtps/', get_smtps_view, name="get_smtps_view"),
    path('delete-smtp/', delete_smtp, name="delete_smtp"),

]
