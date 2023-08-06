from django.urls import path

from web.ecgs import views


urlpatterns = [
    path("ecgs/", views.ECGCreateView.as_view()),
    path("ecgs/<int:pk>/stats/", views.ECGStatsView.as_view()),
]
