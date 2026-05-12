import biosdk
print("biosdk version:", biosdk.__version__ if hasattr(biosdk, '__version__') else '0.1.0')
print("list_adapters():", biosdk.list_adapters())
print("certified_adapters():", biosdk.certified_adapters())
