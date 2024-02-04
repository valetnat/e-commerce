from django.urls import path
from .views import (
    HomePage,
    CustomLoginView,
    AboutUserView,
    UserLogoutView,
    UserRegisterView,
    UserResetPasswordView,
    UserUpdateProfileInfo,
    UserHistoryView,
    CustomPasswordResetView,
    CustomPasswordResetDoneView,
    CustomPasswordResetConfirmView,
    CustomPasswordResetCompleteView,
)

app_name = "profiles"

urlpatterns = [
    path("", HomePage.as_view(), name="home-page"),
    path(
        "login/",
        CustomLoginView.as_view(
            template_name="profiles/login.jinja2",
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("about-user/", AboutUserView.as_view(), name="about-user"),
    path("register/", UserRegisterView.as_view(), name="register"),
    path("change_password/", UserResetPasswordView.as_view(), name="change-password"),
    path("update_info/<int:pk>/", UserUpdateProfileInfo.as_view(), name="update-info"),
    path("history/", UserHistoryView.as_view(), name="browsing_history"),
    path("reset_password/1", CustomPasswordResetView.as_view(), name="reset_password"),
    path("reset_password/2", CustomPasswordResetDoneView.as_view(), name="reset_password_done"),
    path("reset_password/<uidb64>/<token>", CustomPasswordResetConfirmView.as_view(), name="reset_password_confirm"),
    path("reset_password_complete/", CustomPasswordResetCompleteView.as_view(), name="reset_password_complete"),
]
