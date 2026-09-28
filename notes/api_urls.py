from django.urls import path
from . import api_views

urlpatterns = [
    # Auth
    path('auth/login/', api_views.api_login, name='api_login'),
    path('auth/register/', api_views.api_register, name='api_register'),
    path('auth/logout/', api_views.api_logout, name='api_logout'),
    path('auth/me/', api_views.api_me, name='api_me'),

    # Notes
    path('notes/', api_views.api_notes_list, name='api_notes_list'),
    path('notes/create/', api_views.api_note_create, name='api_note_create'),
    path('notes/<int:note_id>/update/', api_views.api_note_update, name='api_note_update'),
    path('notes/<int:note_id>/delete/', api_views.api_note_delete, name='api_note_delete'),
    path('notes/<int:note_id>/toggle/', api_views.api_note_toggle, name='api_note_toggle'),

    # Feedback
    path('feedback/submit/', api_views.api_feedback_submit, name='api_feedback_submit'),
    path('feedback/list/', api_views.api_feedback_list, name='api_feedback_list'),
]
