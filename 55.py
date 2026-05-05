"""
views/quan_ly_cong_dan.py
=========================
Quản lý tổng hợp: ChuSuDung (hồ sơ pháp lý) + User (tài khoản đăng nhập)
Liên kết: User.username == ChuSuDung.so_giay_to
"""
import json
import logging
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from myapp.decorators import admin_required
from myapp.models import ChuSuDung, ThuaDat

logger = logging.getLogger(__name__)
User   = get_user_model()


def _build_row(chu):
    """Gộp ChuSuDung + User thành 1 dict để truyền ra template/JSON."""
    user = User.objects.filter(username=chu.so_giay_to).first()
    so_thua = ThuaDat.objects.filter(danh_sach_chu_su_dung=chu).count()

    return {
        'id':             chu.id,
        'ho_ten':         chu.ho_ten or '—',
        'so_giay_to':     chu.so_giay_to or '—',
        'loai_doi_tuong': chu.loai_doi_tuong,
        'loai_display':   chu.get_loai_doi_tuong_display(),
        'so_dien_thoai':  chu.so_dien_thoai or '',
        'email':          chu.email if hasattr(chu, 'email') else (user.email if user else ''),
        'dia_chi':        chu.dia_chi or '',
        'so_thua':        so_thua,
        # Tài khoản
        'has_account':    user is not None,
        'user_id':        user.id if user else None,
        'is_active':      user.is_active if user else False,
        'is_staff':       user.is_staff if user else False,
        'is_superuser':   user.is_superuser if user else False,
        'last_login':     user.last_login.strftime('%d/%m/%Y %H:%M') if (user and user.last_login) else None,
        'date_joined':    user.date_joined.strftime('%d/%m/%Y') if user else None,
    }


# ─── DANH SÁCH ───────────────────────────────────────────────
@login_required
@admin_required
def danh_sach(request):
    qs = ChuSuDung.objects.all().order_by('ho_ten')

    # Tìm kiếm
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(ho_ten__icontains=q) |
            Q(so_giay_to__icontains=q) |
            Q(so_dien_thoai__icontains=q)
        )

    # Lọc loại đối tượng
    loai = request.GET.get('loai', '').strip()
    if loai:
        qs = qs.filter(loai_doi_tuong=loai)

    # Lọc trạng thái tài khoản
    tk_filter = request.GET.get('tk', '').strip()
    if tk_filter == 'co_tk':
        cccd_list = User.objects.values_list('username', flat=True)
        qs = qs.filter(so_giay_to__in=cccd_list)
    elif tk_filter == 'chua_tk':
        cccd_list = User.objects.values_list('username', flat=True)
        qs = qs.exclude(so_giay_to__in=cccd_list)
    elif tk_filter == 'bi_khoa':
        cccd_list = User.objects.filter(is_active=False).values_list('username', flat=True)
        qs = qs.filter(so_giay_to__in=cccd_list)

    # Phân trang
    paginator = Paginator(qs, 20)
    page      = paginator.get_page(request.GET.get('page', 1))

    # Stats
    tong_chu    = ChuSuDung.objects.count()
    cccd_all    = set(User.objects.values_list('username', flat=True))
    co_tk       = ChuSuDung.objects.filter(so_giay_to__in=cccd_all).count()
    chua_tk     = tong_chu - co_tk
    bi_khoa     = User.objects.filter(is_active=False).count()

    context = {
        'tieu_de_trang': 'Quản lý Công dân & Tài khoản',
        'page_obj':      page,
        'q':             q,
        'loai':          loai,
        'tk_filter':     tk_filter,
        'stats': {
            'tong':    tong_chu,
            'co_tk':   co_tk,
            'chua_tk': chua_tk,
            'bi_khoa': bi_khoa,
        },
    }
    return render(request, 'myapp/quan_ly_cong_dan/index.html', context)


# ─── API: CHI TIẾT 1 CÔNG DÂN ────────────────────────────────
@login_required
@admin_required
def api_chi_tiet(request, pk):
    chu  = get_object_or_404(ChuSuDung, pk=pk)
    data = _build_row(chu)

    # Thêm danh sách thửa đất
    thua_list = []
    for t in ThuaDat.objects.filter(danh_sach_chu_su_dung=chu):
        thua_list.append({
            'id':       t.id,
            'ma_thua':  t.ma_thua,
            'so_to':    t.so_to,
            'so_thua':  t.so_thua,
            'dien_tich': float(t.dien_tich or 0),
            'loai_dat': t.get_loai_dat_hien_trang_display(),
            'dia_chi':  t.dia_chi_thua or '',
        })
    data['danh_sach_thua'] = thua_list
    return JsonResponse(data)


# ─── API: CẬP NHẬT HỒ SƠ PHÁP LÝ ────────────────────────────
@login_required
@admin_required
@require_POST
def api_cap_nhat_ho_so(request, pk):
    chu = get_object_or_404(ChuSuDung, pk=pk)
    try:
        body = json.loads(request.body)
        if body.get('ho_ten'):
            chu.ho_ten = body['ho_ten'].strip()
        if body.get('so_dien_thoai') is not None:
            chu.so_dien_thoai = body['so_dien_thoai'].strip()
        if body.get('dia_chi') is not None:
            chu.dia_chi = body['dia_chi'].strip()
        if body.get('loai_doi_tuong'):
            chu.loai_doi_tuong = body['loai_doi_tuong']
        chu.save()
        return JsonResponse({'ok': True, 'ho_ten': chu.ho_ten})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)


# ─── API: KHÓA / MỞ KHÓA TÀI KHOẢN ─────────────────────────
@login_required
@admin_required
@require_POST
def api_toggle_lock(request, pk):
    chu = get_object_or_404(ChuSuDung, pk=pk)
    user = User.objects.filter(username=chu.so_giay_to).first()
    if not user:
        return JsonResponse({'ok': False, 'error': 'Chưa có tài khoản'}, status=404)
    if user.is_superuser:
        return JsonResponse({'ok': False, 'error': 'Không thể khóa tài khoản Admin'}, status=403)

    user.is_active = not user.is_active
    user.save(update_fields=['is_active'])
    action = 'mở khóa' if user.is_active else 'khóa'
    logger.info(f"Admin {request.user.username} {action} tài khoản {user.username}")
    return JsonResponse({'ok': True, 'is_active': user.is_active})


# ─── API: TẠO TÀI KHOẢN CHO CÔNG DÂN CHƯA CÓ TK ────────────
@login_required
@admin_required
@require_POST
def api_tao_tai_khoan(request, pk):
    chu = get_object_or_404(ChuSuDung, pk=pk)
    if User.objects.filter(username=chu.so_giay_to).exists():
        return JsonResponse({'ok': False, 'error': 'Tài khoản đã tồn tại'}, status=400)

    try:
        body = json.loads(request.body)
        password = body.get('password', chu.so_giay_to)  # default = CCCD
        try:
            validate_password(password)
        except ValidationError as e:
            return JsonResponse({'ok': False, 'error': ' '.join(e.messages)}, status=400)

        user = User.objects.create_user(
            username=chu.so_giay_to,
            password=password,
            first_name=chu.ho_ten,
            email=getattr(chu, 'email', '') or '',
            is_active=True,
            is_staff=False,
        )
        logger.info(f"Admin {request.user.username} tạo TK cho {chu.ho_ten} ({chu.so_giay_to})")
        return JsonResponse({'ok': True, 'user_id': user.id})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)


# ─── API: ADMIN ĐỔI MẬT KHẨU CHO CÔNG DÂN ───────────────────
@login_required
@admin_required
@require_POST
def api_reset_mat_khau(request, pk):
    chu  = get_object_or_404(ChuSuDung, pk=pk)
    user = User.objects.filter(username=chu.so_giay_to).first()
    if not user:
        return JsonResponse({'ok': False, 'error': 'Chưa có tài khoản'}, status=404)

    try:
        body     = json.loads(request.body)
        password = body.get('password', '').strip()
        if len(password) < 6:
            return JsonResponse({'ok': False, 'error': 'Mật khẩu phải từ 6 ký tự'}, status=400)
        try:
            validate_password(password, user)
        except ValidationError as e:
            return JsonResponse({'ok': False, 'error': ' '.join(e.messages)}, status=400)

        user.password = make_password(password)
        user.save(update_fields=['password'])
        logger.info(f"Admin {request.user.username} reset MK cho {user.username}")
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)


# ─── API: XÓA CÔNG DÂN (kèm tài khoản nếu có) ───────────────
@login_required
@admin_required
@require_POST
def api_xoa(request, pk):
    chu = get_object_or_404(ChuSuDung, pk=pk)
    if ThuaDat.objects.filter(danh_sach_chu_su_dung=chu).exists():
        return JsonResponse({'ok': False, 'error': 'Không thể xóa — còn thửa đất liên kết'}, status=400)

    user = User.objects.filter(username=chu.so_giay_to).first()
    if user and user.is_superuser:
        return JsonResponse({'ok': False, 'error': 'Không thể xóa tài khoản Admin'}, status=403)

    ho_ten = chu.ho_ten
    if user:
        user.delete()
    chu.delete()
    logger.info(f"Admin {request.user.username} xóa công dân {ho_ten}")
    return JsonResponse({'ok': True})


# ─── CÔNG DÂN TỰ ĐỔI MẬT KHẨU ──────────────────────────────
@login_required
@require_POST
def api_doi_mat_khau_ca_nhan(request):
    """Công dân tự đổi mật khẩu từ user_dashboard."""
    try:
        body     = json.loads(request.body)
        cu       = body.get('mat_khau_cu', '').strip()
        moi      = body.get('mat_khau_moi', '').strip()
        xac_nhan = body.get('xac_nhan', '').strip()

        if not request.user.check_password(cu):
            return JsonResponse({'ok': False, 'error': 'Mật khẩu hiện tại không đúng'}, status=400)
        if moi != xac_nhan:
            return JsonResponse({'ok': False, 'error': 'Mật khẩu xác nhận không khớp'}, status=400)
        if len(moi) < 6:
            return JsonResponse({'ok': False, 'error': 'Mật khẩu mới phải từ 6 ký tự'}, status=400)

        try:
            validate_password(moi, request.user)
        except ValidationError as e:
            return JsonResponse({'ok': False, 'error': ' '.join(e.messages)}, status=400)

        request.user.set_password(moi)
        request.user.save()
        # Giữ session không bị logout sau khi đổi MK
        from django.contrib.auth import update_session_auth_hash
        update_session_auth_hash(request, request.user)

        logger.info(f"User {request.user.username} đổi mật khẩu thành công")
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)