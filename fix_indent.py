with open('web_app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(473, 686):
    if lines[i].startswith('                '):
        lines[i] = lines[i][4:]
    elif lines[i].startswith('            '):
        lines[i] = lines[i][4:]

with open('web_app.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
