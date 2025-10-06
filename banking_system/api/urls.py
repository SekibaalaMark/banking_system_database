from django.urls import path
from . import views

urlpatterns=[
    path('add_branch/',views.add_branch),
    path('add_employee/',views.add_employee),
]