from django.urls import path

from users_app.api.views import RegistrationView


urlpatterns = [
    path("registration/", RegistrationView.as_view(), name="registration"),
]
