import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from django.db import connection
from apps.tenants.models import ProjectTenant

# Get the real DatabaseWrapper
real_conn = connection._connections['default']

print(f'Before set_tenant:')
print(f'  ConnectionProxy.schema_name = {getattr(connection, "schema_name", "NOT SET")}')
print(f'  DatabaseWrapper.schema_name = {getattr(real_conn, "schema_name", "NOT SET")}')

t = ProjectTenant.objects.get(pk=2)
connection.set_tenant(t)

print(f'After set_tenant:')
print(f'  ConnectionProxy.schema_name = {getattr(connection, "schema_name", "NOT SET")}')
print(f'  DatabaseWrapper.schema_name = {getattr(real_conn, "schema_name", "NOT SET")}')
print(f'  ConnectionProxy.__dict__.keys() = {list(connection.__dict__.keys())}')
print(f'  DatabaseWrapper.__dict__.keys() = {[k for k in real_conn.__dict__.keys() if "schema" in k.lower()]}')

# Now test Client query
from apps.core_engineering.models import Client
try:
    count = Client.objects.count()
    print(f'  Client.objects.count() = {count}')
except Exception as e:
    print(f'  Client.objects.count() ERROR: {e}')
finally:
    connection.set_schema_to_public()
