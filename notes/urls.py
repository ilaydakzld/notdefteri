from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('dashboard/', views.notehome, name='notehome'),
    path('delete/<int:note_id>/', views.note_delete, name='note_delete'),
    path('toggle/<int:note_id>/', views.note_toggle_complete, name='note_toggle_complete'),
    path('edit/<int:note_id>/', views.note_edit, name='note_edit'),
    path('export/', views.export_notes, name='export_notes'),
    path('import/', views.import_notes, name='import_notes'),
    path('register/', views.register, name='register'),
    path('logout/', views.custom_logout, name='logout'),
    path('collab/<str:room_id>/notes/', views.get_collab_notes, name='get_collab_notes'),
    path('collab/<str:room_id>/add/', views.add_collab_note, name='add_collab_note'),
    path('collab/note/<int:note_id>/delete/', views.delete_collab_note, name='delete_collab_note'),
    path('feedback/submit/', views.submit_feedback, name='submit_feedback'),
    path('feedback/my-list/', views.get_user_feedbacks, name='get_user_feedbacks'),
    path('feedback/admin/list/', views.get_admin_feedbacks, name='get_admin_feedbacks'),
    path('feedback/admin/<int:feedback_id>/status/', views.update_feedback_status, name='update_feedback_status'),
    path('feedback/admin/<int:feedback_id>/delete/', views.delete_feedback, name='delete_feedback'),
]
