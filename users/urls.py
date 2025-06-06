from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    # path('teacher-signup/', views.teacher_signup, name='teacher_signup'),
    # path('student-signup/', views.student_signup, name='student_signup'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('accounts/login/', views.login_view, name='login_view'),
    path('register/', views.register_view, name='register_view'),
    
    path('activate/<uidb64>/<token>/', views.activate_account, name='activate_account'),
    
    # path('expert-profile/<str:username>/', views.teacher_profile, name='teacher_profile'),
    # path('sprofile/<str:username>/', views.student_profile, name='student_profile'),
    
    path('profile/<str:username>/', views.teacher_profile, name='teacher_profile'),
    path('learner-profile/<str:username>/', views.student_profile, name='student_profile'),
    
    path('edit-profile/', views.update_teacher_profile, name='update_teacher_profile'),
    path('send-verification-email/', views.send_verification_email, name='send_verification_email'),
    path('pending_verification/', views.pending_verification, name='pending_verification'),
    path('missed-requests/', views.missed_requests_view, name='missed_requests_view'),
    path('logout/', views.logout_view, name='logout'),
    path('cashout/', views.cashout_view, name='cashout_view'),
    
    
    path("send-email/", views.send_email, name="send_email"),
    path("developer/", views.developer_view, name="developer_view"),

    path('teacher/<int:teacher_id>/expertise/', views.TeacherExpertiseListView.as_view(), name='teacher_expertise_list'),
    path('teacher/<int:teacher_id>/expertise/add/', views.TeacherExpertiseCreateView.as_view(), name='teacher_expertise_add'),
    path('teacher/<int:teacher_id>/expertise/<int:pk>/edit/', views.TeacherExpertiseUpdateView.as_view(), name='teacher_expertise_edit'),
    path('teacher/<int:teacher_id>/expertise/<int:pk>/delete/', views.TeacherExpertiseDeleteView.as_view(), name='teacher_expertise_delete'),

    path('change-password/', views.change_password, name='change_password'),
]
