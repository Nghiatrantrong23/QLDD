import sys

with open('user_dashboard_final.html', 'r', encoding='utf-8') as f:
    content = f.read()

old_block = """        <div class="info-row">
          <div class="info-label">Email</div>
          <div class="info-value" style="font-size:12px;word-break:break-all">{{ user_info.email|default:"—" }}</div>
        </div>
        <div class="info-row">
          <div class="info-label">Địa chỉ</div>
          <div class="info-value" style="font-size:12px;text-align:right;max-width:180px">{{ user_info.dia_chi|default:"Chưa có thông tin" }}</div>
        </div>
      </div>
      <button class="update-btn">
        <i class="fa fa-pen-to-square"></i> Cập nhật thông tin
      </button>"""

new_block = """        <div class="info-row">
          <div class="info-label">Email bảo mật</div>
          <div class="info-value" style="font-size:12px;word-break:break-all; text-align: right;">
            {{ user.email }}
            {% if '@nguoidan.gis' in user.email %}
              <div style="font-size:10px; color:var(--rose); margin-top:4px;"><i class="fa fa-triangle-exclamation"></i> Cần cập nhật email thật</div>
            {% endif %}
          </div>
        </div>
        <div class="info-row">
          <div class="info-label">Địa chỉ</div>
          <div class="info-value" style="font-size:12px;text-align:right;max-width:180px">{{ user_info.dia_chi|default:"Chưa có thông tin" }}</div>
        </div>
      </div>

      <div x-data="{ 
          showEmailModal: false, 
          newEmail: '{{ user.email }}',
          async updateEmail() {
              if(!this.newEmail || !this.newEmail.includes('@')) {
                  alert('Email không hợp lệ!'); return;
              }
              try {
                  const res = await fetch('{% url \\'api_cap_nhat_email\\' %}', {
                      method: 'POST',
                      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': '{{ csrf_token }}' },
                      body: JSON.stringify({ email: this.newEmail })
                  });
                  const data = await res.json();
                  if(data.status === 'success') {
                      alert('Đã cập nhật email thành công! Bây giờ bạn có thể dùng email này để nhận link Khôi phục mật khẩu.');
                      window.location.reload();
                  } else {
                      alert(data.message);
                  }
              } catch(e) { alert('Lỗi kết nối máy chủ'); }
          }
      }">
        <button @click="showEmailModal = true" class="update-btn">
          <i class="fa fa-envelope"></i> Cập nhật Email nhận mã
        </button>

        <!-- Modal Cập nhật Email -->
        <div x-show="showEmailModal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.7);z-index:9000;align-items:center;justify-content:center" :style="showEmailModal ? 'display:flex' : 'display:none'">
          <div style="background:var(--surface2);border:1px solid var(--border2);border-radius:var(--radius);padding:28px;max-width:420px;width:90%;position:relative" @click.away="showEmailModal = false">
            <button @click="showEmailModal = false" style="position:absolute;top:14px;right:14px;background:none;border:none;color:var(--text-mid);font-size:18px;cursor:pointer">
              <i class="fa fa-xmark"></i>
            </button>
            <div style="font-family:var(--font-head);font-size:18px;font-weight:700;color:#fff;margin-bottom:18px">
              <i class="fa fa-envelope" style="color:var(--em);margin-right:8px"></i>Cập nhật Email
            </div>
            <p style="font-size:13px; color:var(--text-mid); margin-bottom: 16px;">
              Email này sẽ được sử dụng để nhận đường link Đặt lại mật khẩu. Vui lòng nhập địa chỉ email chính xác của bạn.
            </p>
            <input type="email" x-model="newEmail" placeholder="Nhập email mới..."
              style="width:100%;background:var(--surface3);border:1px solid var(--border2);border-radius:var(--radius-sm);padding:12px;color:var(--text);font-family:var(--font-body);font-size:13px;outline:none;margin-bottom:20px">
            <div style="display:flex;gap:12px;">
              <button @click="showEmailModal = false" style="flex:1;padding:10px;background:transparent;border:1px solid var(--border2);border-radius:var(--radius-sm);color:var(--text);cursor:pointer;font-weight:600">Hủy</button>
              <button @click="updateEmail()" style="flex:1;padding:10px;background:var(--em);border:none;border-radius:var(--radius-sm);color:#fff;cursor:pointer;font-weight:600">Xác nhận</button>
            </div>
          </div>
        </div>
      </div>"""

new_content = content.replace(old_block, new_block)
if old_block not in content:
    print('Failed to replace block!')
    sys.exit(1)

with open('myapp/templates/myapp/nguoi_dung/user_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('Successfully applied design to user_dashboard.html!')
