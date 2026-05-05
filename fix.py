import re
with open(r'd:\lap_trinh_gis\Web_QLDD\myapp\templates\myapp\nguoi_dung\user_dashboard.html', encoding='utf-8') as f:
    text = f.read()

# Fix default filter inside Javascript quotes
text = re.sub(r'default:\\"([^"]*)\\"', r"default:'\1'", text)

# Just in case there's any other space issues, but we only target the specific syntax error
with open(r'd:\lap_trinh_gis\Web_QLDD\myapp\templates\myapp\nguoi_dung\user_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(text)
