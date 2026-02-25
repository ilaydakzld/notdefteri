from django.db import models
from django.contrib.auth.models import User

class Note(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Düşük'),
        ('medium', 'Orta'),
        ('high', 'Yüksek'),
    ]

    CATEGORY_CHOICES = [
        ('personal', 'Kişisel'),
        ('work', 'İş'),
        ('shopping', 'Alışveriş'),
        ('health', 'Sağlık'),
        ('study', 'Eğitim'),
        ('other', 'Diğer'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    tags = models.CharField(max_length=200, blank=True, help_text="Virgülle ayrılmış etiketler")

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_tags_list(self):
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []
