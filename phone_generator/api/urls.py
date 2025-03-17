from django.urls import path

from phone_generator.api.views import clear_numbers_view, delete_all_view, delete_numbers_view, download_csv_view, generate_numbers_view, get_all_numbers_view, get_valid_numbers, total_wipe_view, validate_numbers_view


app_name = 'phone_generator'

urlpatterns = [
    path('generate-numbers/', generate_numbers_view, name="generate_numbers_view"),
    path('clear-numbers/', clear_numbers_view, name="clear_numbers_view"),
    path('delete-all/', delete_all_view, name="delete_all"),
    path('total-wipe/', total_wipe_view, name="total_wipe_view"),
    path('delete-numbers/', delete_numbers_view, name="delete_numbers_view"),
    path('list-numbers/', get_all_numbers_view, name="get_all_numbers_view"),
    path('validate-numbers/', validate_numbers_view, name="validate_numbers_view"),

    path('get-valid-numbers/', get_valid_numbers, name="get_valid_numbers"),
    path('download-numbers/', download_csv_view, name="download_vsc_view"),

]
