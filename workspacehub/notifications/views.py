from django.shortcuts import render, redirect
from django.views.generic import ListView, View
from .models import Notification

class MarkNotificationAsRead(View):
    def post(self, request, notification_id):
        notification = Notification.objects.get(id=notification_id)
        notification.mark_as_read()
        
        return redirect("notifications:notification-list")


class NotificationListView(ListView):
    model = Notification
    context_object_name = "notifications"
    template_name = "notifications/notification_list.html"
    paginate_by = 7
    
    def get_queryset(self):
        return self.request.user.notifications.unread().order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #latest_notifications
        # if self.request.user.is_authenticated:
        latest_notifications = self.request.user.notifications.unread()
        context['latest_notifications'] = latest_notifications[:3]
        context['number_of_notifications'] = latest_notifications.count()
        
        context['header_text'] = "Notifications"
        context['title'] = "All Notifications"
        return context   
