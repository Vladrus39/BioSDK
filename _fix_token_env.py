path = r'biogpu\sdk\external_readonly_v517.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

old = '''TOKEN_ENV_BY_PLATFORM = {
    "finalspark_remote_wetware": "FINALSPARK_TOKEN",
    "threebrain_hdmea": "THREEBRAIN_TOKEN",
    "axion_maestro": "AXION_TOKEN",
    "mcs_mea2100": "MCS_TOKEN",
}'''

new = '''TOKEN_ENV_BY_PLATFORM = {
    "finalspark_remote_wetware": "FINALSPARK_TOKEN",
    "threebrain_hdmea": "THREEBRAIN_TOKEN",
    "axion_maestro": "AXION_TOKEN",
    "mcs_mea2100": "MCS_TOKEN",
    "dandi_archive": None,  # fully open — no token required
}'''

if old in content:
    content = content.replace(old, new)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("TOKEN_ENV_BY_PLATFORM updated successfully")
else:
    print("NOT FOUND — checking what's there...")
    # find the block
    idx = content.find('TOKEN_ENV_BY_PLATFORM')
    if idx >= 0:
        print(repr(content[idx:idx+300]))
