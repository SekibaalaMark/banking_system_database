from django.urls import path
from . import views

urlpatterns=[
    path('add_branch/',views.add_branch),
    path('add_employee/',views.add_employee),
    path('add_account/',views.add_account),
    path('add_customer/',views.add_customer),
    path('make_transaction/',views.make_transaction),
    

]