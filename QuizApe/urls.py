from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('rankedmodel/', include('awl.rankedmodel.urls')),

    path('', core_views.home, name="home"),
    path('<slug:slug>/', core_views.start_quiz, name="start_quiz"),
    path('page/<int:survey_id>/<str:token>/<int:page_num>/', core_views.page,
        name="page"),
    path('done/<int:survey_id>/<str:token>/', core_views.done, name="done"),

    path('duplicate/<int:survey_id>/', core_views.duplicate, name="duplicate"),
    path('result_page/<int:survey_id>/<str:token>/',
        core_views.result_page, name="result_page"),
    path('result_question/<int:q_id>/<str:token>/', core_views.result_question,
        name="result_question"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
