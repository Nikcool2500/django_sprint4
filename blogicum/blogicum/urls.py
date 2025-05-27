from django.urls import path, include
from django.contrib import admin
from django.conf.urls import handler403, handler404, handler500
from blog import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("", include("blog.urls", namespace="blog")),
    path("pages/", include("pages.urls", namespace="pages")),
    path("admin/", admin.site.urls),
    path("auth/", include("django.contrib.auth.urls")),
    path("auth/registration/",
         views.RegistrationView.as_view(), name="registration"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler403 = "pages.views.csrf_failure"
handler404 = "pages.views.page_not_found"
handler500 = "pages.views.server_error"
