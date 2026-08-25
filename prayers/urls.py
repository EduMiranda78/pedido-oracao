from django.contrib.auth import views as auth_views
from django.urls import path

from . import views


urlpatterns = [
    path(
        "manifest.webmanifest",
        views.manifest,
        name="manifest",
    ),

    path(
        "offline/",
        views.offline,
        name="offline",
    ),

    path(
        "health/",
        views.health,
        name="health",
    ),

    path(
        "sw.js",
        views.service_worker,
        name="service_worker",
    ),

    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="registration/login.html",
            redirect_authenticated_user=True,
        ),
        name="login",
    ),

    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),

    path(
        "",
        views.dashboard,
        name="dashboard",
    ),

    path(
        "pedidos/",
        views.prayer_list,
        name="prayer_list",
    ),

    path(
        "pedidos/novo/",
        views.prayer_create,
        name="prayer_create",
    ),

    path(
        "pedidos/<int:pk>/",
        views.prayer_detail,
        name="prayer_detail",
    ),

    path(
        "pedidos/<int:pk>/editar/",
        views.prayer_edit,
        name="prayer_edit",
    ),

    path(
        "imprimir/",
        views.print_list,
        name="print_list",
    ),

    path(
        "exportar/csv/",
        views.export_csv,
        name="export_csv",
    ),

    path(
        "exportar/xlsx/",
        views.export_xlsx,
        name="export_xlsx",
    ),

    path(
        "exportar/pdf/",
        views.export_pdf,
        name="export_pdf",
    ),
]
