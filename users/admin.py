from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CashoutTransaction, ClassLevel, CustomUser, Expertise, Teacher, Student, TeacherExpertise, VidnickContact

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('is_teacher', 'is_student')}),
    )

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('user', 'vidnick_id')
    list_filter = ('verification',)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username',)
    
@admin.register(CashoutTransaction)
class CashoutTransactionAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'amount', 'transaction_id',)
    search_fields = ('teacher__user__username', 'transaction_id')
    
@admin.register(Expertise)
class ExpertiseAdmin(admin.ModelAdmin):
    list_display = ('expertise_name', 'expertise_type')
    list_filter = ('expertise_type',)
    
@admin.register(ClassLevel)
class ClassLevelAdmin(admin.ModelAdmin):
    list_display = ('class_level_name', 'serial')
    list_editable = ('serial',)
    ordering = ('serial',)
    
@admin.register(VidnickContact)
class VidnickContactAdmin(admin.ModelAdmin):
    list_display = ('email', 'telegram_id')
    search_fields = ('email', 'telegram_id')    
    
@admin.register(TeacherExpertise)
class TeacherExpertiseAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'expertise_name')
