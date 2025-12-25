"""
Tenants App - PostgreSQL Schema-based Multi-tenancy

This app implements project-level data isolation using PostgreSQL schemas.
Each project gets its own schema for complete data separation.
"""

default_app_config = 'apps.tenants.apps.TenantsConfig'
