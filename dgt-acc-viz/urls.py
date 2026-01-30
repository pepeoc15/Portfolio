from django.urls import path
from .views import index

app_name = "dgt_acc_viz"

urlpatterns = [
    path("", index, name="index"),
]
