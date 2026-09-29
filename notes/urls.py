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
    path('feedback/admin/<int:feedback_id>/reply/', views.reply_feedback, name='reply_feedback'),
    path('feedback/admin/<int:feedback_id>/delete/', views.delete_feedback, name='delete_feedback'),
    path('exams/list/', views.get_user_exams, name='get_user_exams'),
    path('exams/save/', views.save_user_exam, name='save_user_exam'),
    path('exams/<int:exam_id>/delete/', views.delete_user_exam, name='delete_user_exam'),
    path('exams/<int:exam_id>/pin/', views.toggle_pin_user_exam, name='toggle_pin_user_exam'),
    path('sitemap.xml', views.sitemap_view, name='sitemap'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
]


