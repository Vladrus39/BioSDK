import biosdk
print('Version:', biosdk.__version__)
print('Adapters:', sorted(biosdk.list_adapters()))
print('API functions:')
for f in ['open','features','readout','evidence_bundle','list_adapters','certified_adapters']:
    print(f'  {f}: {callable(getattr(biosdk, f, None))}')
