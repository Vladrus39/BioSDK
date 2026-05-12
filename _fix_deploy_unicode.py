"""Fix Unicode chars in _deploy.py that crash cp1251 console."""
with open('_deploy.py', 'r', encoding='utf-8') as f:
    t = f.read()

t = t.replace('\u2014', '--')   # em dash → double hyphen
t = t.replace('\u2192', '->')   # arrow → ->

with open('_deploy.py', 'w', encoding='utf-8') as f:
    f.write(t)
print("Fixed Unicode chars in _deploy.py")
