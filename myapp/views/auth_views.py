from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth import login
from django.shortcuts import redirect
from myapp.forms import UserRegistrationForm

class UserRegisterView(CreateView):
    template_name = 'myapp/tai_khoan/dang_ky.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('profile_dashboard')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)  # Tự động đăng nhập sau khi đăng ký
        return redirect(self.success_url)

class UserLoginView(LoginView):
    template_name = 'myapp/tai_khoan/dang_nhap.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        if self.request.user.is_superuser:
            return reverse_lazy('tong_quan')
        return reverse_lazy('profile_dashboard')

class UserLogoutView(LogoutView):
    next_page = 'dang_nhap'
