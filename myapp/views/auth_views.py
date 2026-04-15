from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy

class UserLoginView(LoginView):
    template_name = 'myapp/tai_khoan/dang_nhap.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('tong_quan')

class UserLogoutView(LogoutView):
    next_page = 'dang_nhap'
