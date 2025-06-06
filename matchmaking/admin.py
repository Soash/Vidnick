from django.contrib import admin
from .models import RequestHistory, Reports, ExpertiseRequest

@admin.register(RequestHistory)
class RequestHistoryAdmin(admin.ModelAdmin):
    list_display = ('student', 'teacher', 'duration', 'requested_timestamp', 'status')
    list_filter = ('status', )
    # search_fields = ('student__user__username', 'teacher__user__username', 'subject__name')
    # raw_id_fields = ('student', 'teacher', 'subject')
    # readonly_fields = ('timestamp',)


@admin.register(Reports)
class ReportsAdmin(admin.ModelAdmin):
    list_display = ('student', 'teacher', 'description', 'created_at')

@admin.register(ExpertiseRequest)
class ExpertiseRequestAdmin(admin.ModelAdmin):
    list_display = ('description', 'created_at', 'status')
    list_editable = ('status',)
    list_filter = ('status',)
    
    
    
