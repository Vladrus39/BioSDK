f = open(r'biogpu\sdk\external_readonly_v517.py', 'r', encoding='utf-8')
lines = f.readlines()
f.close()
for i, line in enumerate(lines[16:23]):
    print(f"{i+17}: {repr(line)}")
