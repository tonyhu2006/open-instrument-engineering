import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from django.db import connection
from apps.tenants.models import ProjectTenant
from apps.core_engineering.models import Client

# Check current schema before
print(f'Current schema before: {connection.schema_name}')

# Get project 2
t = ProjectTenant.objects.get(pk=2)
print(f'Tenant schema_name: {t.schema_name}')

# Switch to tenant
connection.set_tenant(t)
print(f'Current schema after set_tenant: {connection.schema_name}')

# Try to query Client
try:
    count = Client.objects.count()
    print(f'Client count in tenant schema: {count}')
except Exception as e:
    print(f'ERROR querying Client: {type(e).__name__}: {e}')
finally:
    connection.set_schema_to_public()
    print(f'Schema reset to: {connection.schema_name}')
