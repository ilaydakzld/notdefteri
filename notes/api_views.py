"""
Mobile API endpoints for the Flutter app.
Provides JSON-based authentication, CRUD for notes, feedback, and collab rooms.
"""
import json
from datetime import date, datetime
from functools import wraps

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET

from .models import Note, CollabNote, Feedback


# ─── Auth helpers ────────────────────────────────────────────────
def api_login_required(view_func):
    """Decorator that checks session auth for API views."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'Giriş yapılmamış.'}, status=401)
        return view_func(request, *args, **kwargs)
    return wrapper


def _parse_json_body(request):
    """Parse JSON body from request."""
    try:
        return json.loads(request.body.decode('utf-8')) if request.body else {}
    except Exception:
        return {}


# ─── Auth endpoints ──────────────────────────────────────────────
@csrf_exempt
@require_POST
def api_login(request):
    body = _parse_json_body(request)
    username = body.get('username', '').strip()
    password = body.get('password', '')

    if not username or not password:
        return JsonResponse({'success': False, 'error': 'Kullanıcı adı ve şifre gereklidir.'}, status=400)

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return JsonResponse({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'is_superuser': user.is_superuser,
            }
        })
    return JsonResponse({'success': False, 'error': 'Kullanıcı adı veya şifre hatalı.'}, status=401)


@csrf_exempt
@require_POST
def api_register(request):
    body = _parse_json_body(request)
    username = body.get('username', '').strip()
    password1 = body.get('password1', '')
    password2 = body.get('password2', '')

    if not username or not password1:
        return JsonResponse({'success': False, 'error': 'Kullanıcı adı ve şifre gereklidir.'}, status=400)

    if password1 != password2:
        return JsonResponse({'success': False, 'error': 'Şifreler eşleşmiyor.'}, status=400)

    if len(password1) < 8:
        return JsonResponse({'success': False, 'error': 'Şifre en az 8 karakter olmalıdır.'}, status=400)

    if User.objects.filter(username=username).exists():
        return JsonResponse({'success': False, 'error': 'Bu kullanıcı adı zaten kullanılıyor.'}, status=400)

    try:
        user = User.objects.create_user(username=username, password=password1)
        login(request, user)
        return JsonResponse({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'is_superuser': user.is_superuser,
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@csrf_exempt
@require_POST
def api_logout(request):
    logout(request)
    return JsonResponse({'success': True})


@csrf_exempt
@api_login_required
def api_me(request):
    """Return current user info."""
    user = request.user
    return JsonResponse({
        'success': True,
        'user': {
            'id': user.id,
            'username': user.username,
            'is_superuser': user.is_superuser,
        }
    })


# ─── Notes CRUD ──────────────────────────────────────────────────
@csrf_exempt
@api_login_required
def api_notes_list(request):
    """GET: list all notes for current user with optional filters."""
    notes = Note.objects.filter(user=request.user)

    # Filters
    search = request.GET.get('search', '')
    priority = request.GET.get('priority', '')
    category = request.GET.get('category', '')
    show_completed = request.GET.get('show_completed', 'all')
    filter_type = request.GET.get('filter_type', 'all')

    if search:
        from django.db.models import Q
        notes = notes.filter(
            Q(title__icontains=search) |
            Q(content__icontains=search) |
            Q(tags__icontains=search)
        )

    if priority:
        notes = notes.filter(priority=priority)
    if category:
        notes = notes.filter(category=category)

    if show_completed == 'completed':
        notes = notes.filter(is_completed=True)
    elif show_completed == 'active':
        notes = notes.filter(is_completed=False)

    today_date = date.today()
    if filter_type == 'today':
        notes = notes.filter(due_date=today_date)
    elif filter_type == 'overdue':
        notes = notes.filter(due_date__lt=today_date, is_completed=False)

    data = []
    for note in notes:
        data.append({
            'id': note.id,
            'title': note.title,
            'content': note.content,
            'created_at': note.created_at.isoformat(),
            'updated_at': note.updated_at.isoformat(),
            'due_date': note.due_date.isoformat() if note.due_date else None,
            'is_completed': note.is_completed,
            'priority': note.priority,
            'category': note.category,
            'tags': note.tags,
        })

    # Stats
    all_notes = list(Note.objects.filter(user=request.user))
    total = len(all_notes)
    completed = sum(1 for n in all_notes if n.is_completed)
    active = total - completed
    overdue = sum(1 for n in all_notes if not n.is_completed and n.due_date and n.due_date < today_date)
    today_count = sum(1 for n in all_notes if n.due_date == today_date)
    high_priority = sum(1 for n in all_notes if not n.is_completed and n.priority == 'high')

    return JsonResponse({
        'success': True,
        'notes': data,
        'stats': {
            'total': total,
            'completed': completed,
            'active': active,
            'overdue': overdue,
            'today': today_count,
            'high_priority': high_priority,
        }
    })


@csrf_exempt
@api_login_required
@require_POST
def api_note_create(request):
    body = _parse_json_body(request)
    title = body.get('title', '').strip()
    content = body.get('content', '').strip()
    due_date = body.get('due_date')
    priority = body.get('priority', 'medium')
    category = body.get('category', 'other')
    tags = body.get('tags', '')

    if not title:
        return JsonResponse({'success': False, 'error': 'Başlık gereklidir.'}, status=400)

    note_data = {
        'user': request.user,
        'title': title,
        'content': content,
        'priority': priority,
        'category': category,
        'tags': tags,
    }
    if due_date:
        note_data['due_date'] = due_date

    note = Note.objects.create(**note_data)
    return JsonResponse({
        'success': True,
        'note': {
            'id': note.id,
            'title': note.title,
            'content': note.content,
            'created_at': note.created_at.isoformat(),
            'updated_at': note.updated_at.isoformat(),
            'due_date': note.due_date.isoformat() if note.due_date else None,
            'is_completed': note.is_completed,
            'priority': note.priority,
            'category': note.category,
            'tags': note.tags,
        }
    })


@csrf_exempt
@api_login_required
@require_POST
def api_note_update(request, note_id):
    from django.shortcuts import get_object_or_404
    note = get_object_or_404(Note, id=note_id, user=request.user)
    body = _parse_json_body(request)

    note.title = body.get('title', note.title).strip()
    note.content = body.get('content', note.content)
    note.priority = body.get('priority', note.priority)
    note.category = body.get('category', note.category)
    note.tags = body.get('tags', note.tags)

    due_date = body.get('due_date')
    if due_date == '':
        note.due_date = None
    elif due_date:
        note.due_date = due_date

    note.save()
    return JsonResponse({
        'success': True,
        'note': {
            'id': note.id,
            'title': note.title,
            'content': note.content,
            'created_at': note.created_at.isoformat(),
            'updated_at': note.updated_at.isoformat(),
            'due_date': note.due_date.isoformat() if note.due_date else None,
            'is_completed': note.is_completed,
            'priority': note.priority,
            'category': note.category,
            'tags': note.tags,
        }
    })


@csrf_exempt
@api_login_required
@require_POST
def api_note_delete(request, note_id):
    from django.shortcuts import get_object_or_404
    note = get_object_or_404(Note, id=note_id, user=request.user)
    note.delete()
    return JsonResponse({'success': True})


@csrf_exempt
@api_login_required
@require_POST
def api_note_toggle(request, note_id):
    from django.shortcuts import get_object_or_404
    note = get_object_or_404(Note, id=note_id, user=request.user)
    note.is_completed = not note.is_completed
    note.save()
    return JsonResponse({
        'success': True,
        'is_completed': note.is_completed,
    })


# ─── Feedback endpoints ─────────────────────────────────────────
@csrf_exempt
@api_login_required
@require_POST
def api_feedback_submit(request):
    body = _parse_json_body(request)
    subject = body.get('subject', '').strip()
    message = body.get('message', '').strip()

    if not subject or not message:
        return JsonResponse({'success': False, 'error': 'Konu ve mesaj zorunludur.'}, status=400)

    Feedback.objects.create(
        user=request.user,
        user_name=request.user.username or 'Anonim',
        subject=subject,
        message=message
    )
    return JsonResponse({'success': True, 'message': 'Geri bildiriminiz başarıyla alındı.'})


@csrf_exempt
@api_login_required
def api_feedback_list(request):
    feedbacks = Feedback.objects.filter(user=request.user).order_by('-created_at')
    data = []
    for f in feedbacks:
        data.append({
            'id': f.id,
            'subject': f.subject,
            'message': f.message,
            'status': f.status,
            'status_display': f.get_status_display(),
            'admin_reply': f.admin_reply,
            'replied_at': f.replied_at.strftime('%d.%m.%Y %H:%M') if f.replied_at else None,
            'date': f.created_at.strftime('%d.%m.%Y %H:%M'),
        })
    return JsonResponse({'success': True, 'feedbacks': data})
