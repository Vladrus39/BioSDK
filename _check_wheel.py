import zipfile
z = zipfile.ZipFile('dist/biosdk-0.1.0-py3-none-any.whl')
dandi = [n for n in z.namelist() if 'dandi' in n]
nsi = [n for n in z.namelist() if 'nsi' in n]
print("DANDI files in wheel:", dandi)
print("NSI files in wheel:", nsi)
print(f"Total files: {len(z.namelist())}")
print(f"Wheel size: {sum(z.getinfo(n).file_size for n in z.namelist()) / 1024:.0f} KB")
