from django.urls import path
from . import views

urlpatterns = [
    path('', views.notehome, name='notehome'),
    path('delete/<int:note_id>/', views.note_delete, name='note_delete'),
    path('toggle/<int:note_id>/', views.note_toggle_complete, name='note_toggle_complete'),
    path('edit/<int:note_id>/', views.note_edit, name='note_edit'),
    path('export/', views.export_notes, name='export_notes'),
    path('import/', views.import_notes, name='import_notes'),
    path('register/', views.register, name='register'),
    path('logout/', views.custom_logout, name='logout'),
]