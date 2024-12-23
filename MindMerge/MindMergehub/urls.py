from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("login/", views.loginPage, name="login"),
    path("logout/", views.logoutUser, name="logout"),
    path("register/", views.registerPage, name="register"),
    path("verify-email/", views.verifyEmail, name="verify_email"),
    path("home", views.home, name="home"),
    path("", views.base, name="base"),
    path("about/", views.about, name="about"),
    path("contacts/", views.contacts, name="contacts"),
    path("topics", views.topics, name="topics"),
    path("room/<str:pk>/", views.room, name="room"),
    path("create-room/", views.createRoom, name="create-room"),
    path("update-room/<str:pk>/", views.updateRoom, name="update-room"),
    path("delete-room/<str:pk>/", views.deleteRoom, name="delete-room"),
    path("delete-comment/<str:pk>/", views.deleteComment, name="delete-comment"),
    path("profile/<str:pk>", views.userProfile, name="profile"),
    path("update-user/", views.updateUser, name="update-user"),
    path("delete-profile/", views.deleteProfile, name="delete-profile"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)