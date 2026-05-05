import re
content = open(r'd:\lap_trinh_gis\Web_QLDD\myapp\templates\myapp\nguoi_dung\user_dashboard.html', encoding='utf-8').read()
content = re.sub(r'default:\\"([^"]*)\\"', r"default:'\1'\", content)
open(r'd:\lap_trinh_gis\Web_QLDD\myapp\templates\myapp\nguoi_dung\user_dashboard.html', 'w', encoding='utf-8').write(content)
