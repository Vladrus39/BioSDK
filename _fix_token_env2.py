path = r'biogpu\sdk\external_readonly_v517.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

old = "    configured_tokens = [env_name for env_name in TOKEN_ENV_BY_PLATFORM.values() if os.environ.get(env_name)]"
new = "    configured_tokens = [env_name for env_name in TOKEN_ENV_BY_PLATFORM.values() if env_name and os.environ.get(env_name)]"

if old in content:
    content = content.replace(old, new)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Fixed configured_tokens line")
else:
    print("NOT FOUND")
    idx = content.find('configured_tokens')
    if idx >= 0:
        print(content[idx:idx+120])
