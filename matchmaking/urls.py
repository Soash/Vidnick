from django.urls import path
from . import views

urlpatterns = [
    
    path('find-teacher/', views.SearchTeacher.as_view(), name='find_teacher'),
    path('browse-teacher/', views.SearchTeacher.as_view(), name='browse_teacher'),
    
    path('session/<int:pk>/', views.RequestHistoryDetailView.as_view(), name='request_history_detail'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    
    path('accept-request/<int:request_history_id>/', views.accept_request, name='accept_request'),
    path('assign-teacher/<int:request_history_id>/<int:teacher_id>/', views.assign_teacher, name='assign_teacher'),
    path('delete-teacher/<int:request_history_id>/<int:teacher_id>/', views.delete_teacher, name='delete_teacher'),
    
    path('meeting-log/<int:request_history_id>/', views.meeting_log, name='meeting_log'),
    path('save-token/', views.save_token, name='save_token'),

    path('start-meeting/<int:request_id>/', views.start_jitsi_meeting, name='start_jitsi_meeting'),
    path('join-meeting/<int:request_id>/', views.join_jitsi_meeting, name='join_jitsi_meeting'),
    path('end-meeting/<str:meeting_id>/', views.meeting_end, name='meeting_end'),
    
    path('send-demo-notification/', views.send_demo_notification, name='send_demo_notification'),
    
    
    path('submit-rating/<int:request_id>/', views.submit_rating, name='submit_rating'),
    path('submit-report/<int:request_id>/', views.submit_report, name='submit_report'),
    path('request-subject-skill', views.request_subject_skill, name='request_subject_skill'),
    
    path('initiate-payment/<int:request_id>/', views.initiate_payment, name='initiate_payment'),
    path('initiate-refund/<int:request_id>/', views.initiate_refund, name='initiate_refund'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('payment-fail/', views.payment_fail, name='payment_fail'),
    path('payment-cancel/', views.payment_cancel, name='payment_cancel'),
]

