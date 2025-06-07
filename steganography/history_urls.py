from django.urls import path
from . import views

app_name = 'history'

urlpatterns = [
    path('', views.history_view, name='history'),
    path('detail/<int:operation_id>/', views.history_detail, name='detail'),
    path('delete/<int:operation_id>/', views.history_delete, name='delete'),
]

