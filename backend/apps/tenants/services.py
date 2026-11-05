"""
ProjectTenant service — ADM-T02 lifecycle and §15.4.6 default hierarchy.
"""

from __future__ import annotations

from django_tenants.utils import schema_context

from apps.core.services import CrudService

from . import hierarchy_config
from .models import ProjectTenant


class ProjectTenantService(CrudService):
    model = ProjectTenant
    error_prefix = "ADM"

    def create(self, data, *, batch_id=None):
        data = dict(data)
        if not data.get("organization_id") and self.user is not None:
            data["organization_id"] = getattr(self.user, "organization_id", None)
        data["hierarchy_config"] = hierarchy_config.normalize(
            data.get("hierarchy_config"), for_new_project=True
        )
        return super().create(data, batch_id=batch_id)

    def update(self, instance, data, **kwargs):
        data = dict(data)
        if "hierarchy_config" in data:
            data["hierarchy_config"] = hierarchy_config.normalize(
                data["hierarchy_config"], for_new_project=False
            )
        return super().update(instance, data, require_version=False, **kwargs)

    def before_save(self, instance, *, creating, data):
        if creating and not instance.schema_name:
            instance.schema_name = ProjectTenant.schema_name_for(instance.project_no)

    def after_save(self, instance, *, creating, data):
        if creating:
            self.create_default_hierarchy(instance)

    def create_default_hierarchy(self, project: ProjectTenant) -> list:
        """§15.4.6 step ③: create the default Client → Site → Plant chain."""
        levels = hierarchy_config.default_levels_to_create(project.hierarchy_config)
        if not levels:
            return []
        from apps.core_engineering.services import (
            ClientService,
            PlantService,
            SiteService,
        )

        created = []
        with schema_context(project.schema_name):
            parent = None
            for level in levels:
                values = {"code": level["code"], "name": level["default_name"]}
                if level["name"] == "Client":
                    parent = ClientService(user=self.user, request=self.request).create(
                        values
                    )
                elif level["name"] == "Site":
                    parent = SiteService(user=self.user, request=self.request).create(
                        {**values, "client": parent}
                    )
                elif level["name"] == "Plant":
                    parent = PlantService(user=self.user, request=self.request).create(
                        {**values, "site": parent}
                    )
                created.append(parent)
        return created
