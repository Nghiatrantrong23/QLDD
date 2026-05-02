from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from myapp.decorators import admin_required
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Q
from django.contrib import messages
from myapp.models import NguoiDungProfile
from django.core.paginator import Paginator
import json

def is_admin(user):
    return user.is_superuser

@login_required
@admin_required
def danh_sach_nguoi_dung(request):
    """Bảng điều khiển quản lý tài khoản"""
    # 1. Thống kê
    stats = {
        'total': User.objects.count(),
        'active': User.objects.filter(is_active=True, system_profile__is_locked=False).count(),
        'locked': NguoiDungProfile.objects.filter(is_locked=True).count(),
        'admin': NguoiDungProfile.objects.filter(vai_tro='admin').count(),
        'can_bo': NguoiDungProfile.objects.filter(vai_tro='can_bo').count(),
        'nguoi_dung': NguoiDungProfile.objects.filter(vai_tro='nguoi_dung').count(),
    }

    # 2. Lọc & Tìm kiếm
    query = request.GET.get('q', '')
    role = request.GET.get('role', '')
    status = request.GET.get('status', '')

    users = User.objects.select_related('system_profile').all()

    if query:
        users = users.filter(
            Q(username__icontains=query) | 
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )
    
    if role:
        users = users.filter(system_profile__vai_tro=role)
    
    if status == 'locked':
        users = users.filter(system_profile__is_locked=True)
    elif status == 'active':
        users = users.filter(system_profile__is_locked=False, is_active=True)

    # 3. Phân trang
    paginator = Paginator(users.order_by('-date_joined'), 10)
    trang = request.GET.get('trang', 1)
    danh_sach = paginator.get_page(trang)

    context = {
        'tieu_de_trang': 'Quản lý tài khoản',
        'danh_sach': danh_sach,
        'stats': stats,
        'query': query,
        'role_filter': role,
        'status_filter': status,
    }
    return render(request, 'myapp/nguoi_dung/danh_sach.html', context)

@login_required
@admin_required
def them_nguoi_dung(request):
    """Thêm tài khoản mới"""
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            fullname = request.POST.get('fullname')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            password = request.POST.get('password')
            role = request.POST.get('role', 'nguoi_dung')
            khu_vuc = request.POST.get('khu_vuc', '')
            status = request.POST.get('status', 'active') # active hoặc locked

            if User.objects.filter(username=username).exists():
                messages.error(request, 'Tên đăng nhập đã tồn tại')
                return redirect('nd_danh_sach')

            user = User.objects.create_user(username=username, email=email, password=password)
            
            # Tên đầy đủ
            name_parts = fullname.split(' ', 1)
            user.first_name = name_parts[1] if len(name_parts) > 1 else fullname
            user.last_name = name_parts[0] if len(name_parts) > 1 else ""
            
            # Phân quyền Django chuẩn
            user.is_staff = (role in ['admin', 'can_bo'])
            user.is_superuser = (role == 'admin')
            user.save()

            # Profile cập nhật (đã được tạo bởi signal)
            profile = user.system_profile
            profile.so_dien_thoai = phone
            profile.vai_tro = role
            profile.khu_vuc_phu_trach = khu_vuc
            profile.is_locked = (status == 'locked')
            profile.save()

            # Đồng bộ is_active
            user.is_active = not profile.is_locked
            user.save()

            messages.success(request, f'Đã thêm tài khoản {username} thành công.')
        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')
            
    return redirect('nd_danh_sach')

@login_required
@admin_required
def chinh_sua_nguoi_dung(request, pk):
    """Sửa tài khoản"""
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        try:
            fullname = request.POST.get('fullname')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            role = request.POST.get('role')
            khu_vuc = request.POST.get('khu_vuc', '')

            user.email = email
            name_parts = fullname.split(' ', 1)
            user.first_name = name_parts[1] if len(name_parts) > 1 else fullname
            user.last_name = name_parts[0] if len(name_parts) > 1 else ""
            
            user.is_staff = (role in ['admin', 'can_bo'])
            user.is_superuser = (role == 'admin')
            user.save()

            profile = user.system_profile
            profile.so_dien_thoai = phone
            profile.vai_tro = role
            profile.khu_vuc_phu_trach = khu_vuc
            profile.save()

            messages.success(request, 'Cập nhật tài khoản thành công.')
        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')
            
    return redirect('nd_danh_sach')

@login_required
@admin_required
def xoa_nguoi_dung(request, pk):
    """Xóa tài khoản"""
    if request.method == 'POST':
        user = get_object_or_404(User, pk=pk)
        if user.is_superuser and User.objects.filter(is_superuser=True).count() <= 1:
            messages.error(request, 'Không thể xóa tài khoản Quản trị cuối cùng.')
        else:
            username = user.username
            user.delete()
            messages.success(request, f'Đã xóa tài khoản {username}.')
    return redirect('nd_danh_sach')

@login_required
@admin_required
def api_thao_tac_tai_khoan(request):
    """Thao tác nhanh: Khóa/Mở khóa hoặc Reset mật khẩu"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            action = data.get('action')
            user_id = data.get('user_id')
            user = get_object_or_404(User, pk=user_id)
            
            if action == 'toggle_lock':
                profile = user.system_profile
                profile.is_locked = not profile.is_locked
                profile.save()
                user.is_active = not profile.is_locked
                user.save()
                return JsonResponse({'status': 'success', 'is_locked': profile.is_locked})
            
            elif action == 'reset_password':
                new_password = data.get('password')
                if not new_password or len(new_password) < 6:
                    return JsonResponse({'status': 'error', 'message': 'Mật khẩu quá ngắn'}, status=400)
                user.set_password(new_password)
                user.save()
                return JsonResponse({'status': 'success', 'message': 'Đã cấp lại mật khẩu mới.'})
                
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return HttpResponseForbidden()
