from django.urls import path
from . import views

urlpatterns = [
    path("general-results/", views.general_results, name="general_results"),
    path("results-for-period/", views.results_for_period, name="results_for_period"),
    path("compare_periods/", views.compare_periods, name="compare_periods"),
]
