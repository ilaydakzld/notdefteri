from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from .models import Note, CollabNote, Feedback
from django.db.models import Q, Count


from django.http import JsonResponse, HttpResponse
from datetime import date, datetime, timedelta
import json

def custom_logout(request):
    logout(request)
    return redirect('login')

@login_required
def notehome(request):
    if request.method == 'POST':
        title = request.POST['title']
        content = request.POST['content']
        due_date = request.POST.get('due_date')
        priority = request.POST.get('priority', 'medium')
        category = request.POST.get('category', 'other')
        tags = request.POST.get('tags', '')

        note_data = {
            'user': request.user,
            'title': title,
            'content': content,
            'priority': priority,
            'category': category,
            'tags': tags
        }

        if due_date:
            note_data['due_date'] = due_date

        Note.objects.create(**note_data)
        return redirect('notehome')

    notes = Note.objects.filter(user=request.user)

    # Filtreleme seçenekleri
    filter_type = request.GET.get('filter_type', 'all')
    search_query = request.GET.get('search', '')
    search_date = request.GET.get('search_date')
    due_date_filter = request.GET.get('due_date_filter')
    show_completed = request.GET.get('show_completed', 'all')
    priority_filter = request.GET.get('priority')
    category_filter = request.GET.get('category')
    tag_filter = request.GET.get('tag')

    # Arama
    if search_query:
        notes = notes.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(tags__icontains=search_query)
        )

    # Önem filtresi
    if priority_filter:
        notes = notes.filter(priority=priority_filter)

    # Kategori filtresi
    if category_filter:
        notes = notes.filter(category=category_filter)

    # Etiket filtresi
    if tag_filter:
        notes = notes.filter(tags__icontains=tag_filter)

    # Tarihe göre arama (oluşturulma tarihi)
    if search_date:
        search_datetime = datetime.strptime(search_date, '%Y-%m-%d').date()
        notes = notes.filter(created_at__date=search_datetime)

    # Bitiş tarihine göre filtreleme
    if due_date_filter:
        due_datetime = datetime.strptime(due_date_filter, '%Y-%m-%d').date()
        notes = notes.filter(due_date=due_datetime)

    # Bugün, bu hafta, gelecek filtreler
    if filter_type == 'today':
        notes = notes.filter(due_date=date.today())
    elif filter_type == 'week':
        start_date = date.today()
        end_date = start_date + timedelta(days=7)
        notes = notes.filter(due_date__range=[start_date, end_date])
    elif filter_type == 'overdue':
        notes = notes.filter(due_date__lt=date.today(), is_completed=False)

    # Tamamlanma durumuna göre filtreleme
    if show_completed == 'completed':
        notes = notes.filter(is_completed=True)
    elif show_completed == 'active':
        notes = notes.filter(is_completed=False)

    # İstatistikler
    user_notes = Note.objects.filter(user=request.user)
    stats = {
        'total': user_notes.count(),
        'completed': user_notes.filter(is_completed=True).count(),
        'active': user_notes.filter(is_completed=False).count(),
        'overdue': user_notes.filter(due_date__lt=date.today(), is_completed=False).count(),
        'today': user_notes.filter(due_date=date.today()).count(),
        'high_priority': user_notes.filter(priority='high', is_completed=False).count(),
    }

    # Kategorilere göre gruplama
    categories = user_notes.values('category').annotate(count=Count('category'))

    # Tüm etiketleri al
    all_tags = set()
    for note in user_notes:
        all_tags.update(note.get_tags_list())

    return render(request, 'notehome.html', {
        'notes': notes,
        'filter_type': filter_type,
        'show_completed': show_completed,
        'today': date.today(),
        'stats': stats,
        'categories': categories,
        'all_tags': sorted(all_tags),
        'Note': Note,
    })

@login_required
def note_delete(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)
    note.delete()
    return redirect('notehome')

@login_required
def note_toggle_complete(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)
    note.is_completed = not note.is_completed
    note.save()
    return redirect('notehome')

@login_required
def note_edit(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)

    if request.method == 'POST':
        note.title = request.POST['title']
        note.content = request.POST['content']
        note.priority = request.POST.get('priority', 'medium')
        note.category = request.POST.get('category', 'other')
        note.tags = request.POST.get('tags', '')
        due_date = request.POST.get('due_date')

        if due_date:
            note.due_date = due_date
        else:
            note.due_date = None

        note.save()
        return redirect('notehome')

    return render(request, 'note_edit.html', {'note': note, 'Note': Note})

@login_required
def export_notes(request):
    notes = Note.objects.filter(user=request.user)
    notes_data = []

    for note in notes:
        notes_data.append({
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

    response = HttpResponse(
        json.dumps(notes_data, ensure_ascii=False, indent=2),
        content_type='application/json'
    )
    response['Content-Disposition'] = f'attachment; filename="notes_{date.today()}.json"'
    return response

@login_required
def import_notes(request):
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            file = request.FILES['file']
            data = json.loads(file.read().decode('utf-8'))

            imported_count = 0
            for note_data in data:
                note = Note(
                    user=request.user,
                    title=note_data.get('title', 'Başlıksız'),
                    content=note_data.get('content', ''),
                    priority=note_data.get('priority', 'medium'),
                    category=note_data.get('category', 'other'),
                    tags=note_data.get('tags', ''),
                    is_completed=note_data.get('is_completed', False),
                )

                if note_data.get('due_date'):
                    note.due_date = datetime.fromisoformat(note_data['due_date']).date()

                note.save()
                imported_count += 1

            return JsonResponse({'success': True, 'count': imported_count})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'No file provided'})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('notehome')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


def landing(request):
    if request.user.is_authenticated:
        return redirect('notehome')
    return render(request, 'landing.html')


@login_required
def get_collab_notes(request, room_id):
    room_id = room_id.strip().upper()
    notes = CollabNote.objects.filter(room_id=room_id).order_by('-created_at')
    data = []
    for n in notes:
        data.append({
            'id': n.id,
            'title': n.title,
            'content': n.content,
            'author': n.author_name or (n.author.username if n.author else 'Anonim'),
            'date': n.created_at.strftime('%d.%m.%Y %H:%M')
        })
    return JsonResponse({'success': True, 'notes': data})


@login_required
def add_collab_note(request, room_id):
    if request.method == 'POST':
        try:
            body = json.loads(request.body.decode('utf-8')) if request.body else {}
            title = body.get('title', '').strip()
            content = body.get('content', '').strip()
        except Exception:
            title = request.POST.get('title', '').strip()
            content = request.POST.get('content', '').strip()

        if not title:
            return JsonResponse({'success': False, 'error': 'Başlık gereklidir.'}, status=400)

        room_id = room_id.strip().upper()
        author_name = request.user.username if request.user.is_authenticated else 'Anonim'

        note = CollabNote.objects.create(
            room_id=room_id,
            author=request.user if request.user.is_authenticated else None,
            author_name=author_name,
            title=title,
            content=content
        )
        return JsonResponse({
            'success': True,
            'note': {
                'id': note.id,
                'title': note.title,
                'content': note.content,
                'author': note.author_name,
                'date': note.created_at.strftime('%d.%m.%Y %H:%M')
            }
        })
    return JsonResponse({'success': False, 'error': 'Geçersiz yöntem.'}, status=405)


@login_required
def delete_collab_note(request, note_id):
    if request.method == 'POST':
        note = get_object_or_404(CollabNote, id=note_id)
        note.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Geçersiz yöntem.'}, status=405)


@login_required
def submit_feedback(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body.decode('utf-8')) if request.body else {}
            subject = body.get('subject', '').strip()
            message = body.get('message', '').strip()
        except Exception:
            subject = request.POST.get('subject', '').strip()
            message = request.POST.get('message', '').strip()

        if not subject or not message:
            return JsonResponse({'success': False, 'error': 'Konu ve mesaj zorunludur.'}, status=400)

        Feedback.objects.create(
            user=request.user,
            user_name=request.user.username or 'Anonim',
            subject=subject,
            message=message
        )
        return JsonResponse({'success': True, 'message': 'Geri bildiriminiz başarıyla alındı.'})
    return JsonResponse({'success': False, 'error': 'Geçersiz yöntem.'}, status=405)


@login_required
def get_user_feedbacks(request):
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
            'date': f.created_at.strftime('%d.%m.%Y %H:%M')
        })
    return JsonResponse({'success': True, 'feedbacks': data})


@login_required
def get_admin_feedbacks(request):
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Bu işlem için yetkiniz yoktur.'}, status=403)

    status_filter = request.GET.get('status', 'all')
    feedbacks = Feedback.objects.all().order_by('-created_at')
    if status_filter in ['pending', 'in_progress', 'resolved']:
        feedbacks = feedbacks.filter(status=status_filter)

    data = []
    for f in feedbacks:
        data.append({
            'id': f.id,
            'user': f.user_name or (f.user.username if f.user else 'Anonim'),
            'subject': f.subject,
            'message': f.message,
            'status': f.status,
            'status_display': f.get_status_display(),
            'admin_reply': f.admin_reply,
            'replied_at': f.replied_at.strftime('%d.%m.%Y %H:%M') if f.replied_at else None,
            'date': f.created_at.strftime('%d.%m.%Y %H:%M')
        })

    stats = {
        'total': Feedback.objects.count(),
        'pending': Feedback.objects.filter(status='pending').count(),
        'in_progress': Feedback.objects.filter(status='in_progress').count(),
        'resolved': Feedback.objects.filter(status='resolved').count(),
    }

    return JsonResponse({'success': True, 'feedbacks': data, 'stats': stats})


@login_required
def update_feedback_status(request, feedback_id):
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Bu işlem için yetkiniz yoktur.'}, status=403)

    if request.method == 'POST':
        try:
            body = json.loads(request.body.decode('utf-8')) if request.body else {}
            new_status = body.get('status')
        except Exception:
            new_status = request.POST.get('status')

        if new_status not in ['pending', 'in_progress', 'resolved']:
            return JsonResponse({'success': False, 'error': 'Geçersiz durum.'}, status=400)

        feedback = get_object_or_404(Feedback, id=feedback_id)
        feedback.status = new_status
        feedback.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Geçersiz yöntem.'}, status=405)


@login_required
def reply_feedback(request, feedback_id):
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Bu işlem için yetkiniz yoktur.'}, status=403)

    if request.method == 'POST':
        try:
            body = json.loads(request.body.decode('utf-8')) if request.body else {}
            reply_text = body.get('reply', '').strip()
        except Exception:
            reply_text = request.POST.get('reply', '').strip()

        if not reply_text:
            return JsonResponse({'success': False, 'error': 'Cevap metni boş olamaz.'}, status=400)

        feedback = get_object_or_404(Feedback, id=feedback_id)
        feedback.admin_reply = reply_text
        feedback.replied_at = datetime.now()
        if feedback.status == 'pending':
            feedback.status = 'in_progress'
        feedback.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Geçersiz yöntem.'}, status=405)


@login_required
def delete_feedback(request, feedback_id):
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Bu işlem için yetkiniz yoktur.'}, status=403)

    if request.method == 'POST':
        feedback = get_object_or_404(Feedback, id=feedback_id)
        feedback.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Geçersiz yöntem.'}, status=405)





