from django.urls import path
from . import views
from .views import get_store_data

urlpatterns = [
    path('get_data_by_store/<int:store_id>/', get_store_data, name='get_store_data'),
]
