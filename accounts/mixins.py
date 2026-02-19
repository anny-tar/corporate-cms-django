from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied


class AdminRequiredMixin(UserPassesTestMixin):
    """
    Миксин для контроллеров, доступных только администратору
    """
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        return self.request.user.role == 'admin'
    
    def handle_no_permission(self):
        raise PermissionDenied("Доступ только для администратора")


class ContentManagerRequiredMixin(UserPassesTestMixin):
    """
    Миксин для контроллеров, доступных контент-менеджеру и администратору
    """
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        return self.request.user.role in ['admin', 'content_manager']
    
    def handle_no_permission(self):
        raise PermissionDenied("Доступ только для контент-менеджеров и администратора")


class CRMManagerRequiredMixin(UserPassesTestMixin):
    """
    Миксин для контроллеров, доступных CRM-менеджеру и администратору
    """
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        return self.request.user.role in ['admin', 'crm_manager']
    
    def handle_no_permission(self):
        raise PermissionDenied("Доступ только для CRM-менеджеров и администратора")