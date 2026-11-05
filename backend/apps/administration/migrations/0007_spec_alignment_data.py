"""
SPECIFICATION Module 15 alignment — data step.

1. Organization slugs (unique).
2. Task-force codes become globally unique (duplicates get a ``-<id>`` suffix).
3. One task force per project (§15.3.1): for every project with several
   groups the oldest is kept; members of the others are merged into it and
   the others are detached (project emptied) and deactivated — nobody loses
   access to a project they could see before.
4. Memberships: ``joined_at`` = ``created_at``; legacy role "leader" becomes
   the group leader when none is set.
5. Decision D5: the 7 system roles of every organization (data migration),
   and users without a role get their organization's GUEST role
   (§15.2.3 "every user must have a system role").
6. Users must have unique e-mail addresses (§15.2.3); duplicates abort the
   migration with a list so they can be fixed by hand.
"""

from collections import defaultdict

from django.db import migrations
from django.utils.text import slugify


def _unique_slugs(Organization):
    used = set()
    for org in Organization.objects.order_by("pk"):
        base = slugify(org.code, allow_unicode=True)[:50] or f"org-{org.pk}"
        slug, n = base, 1
        while slug in used:
            n += 1
            slug = f"{base}-{n}"
        used.add(slug)
        if org.slug != slug:
            org.slug = slug
            org.save(update_fields=["slug"])


def _task_forces(ProjectTaskForce, TaskForceMembership):
    seen = set()
    for tf in ProjectTaskForce.objects.order_by("pk"):
        changed = []
        if tf.project_id == 0:
            tf.project_id = None
            changed.append("project_id")
        if tf.code in seen:
            tf.code = f"{tf.code}-{tf.pk}"[:50]
            changed.append("code")
        seen.add(tf.code)
        if changed:
            tf.save(update_fields=changed)

    # Legacy "leader" memberships first, so each group keeps its own leader
    # before duplicate groups are merged.
    for membership in TaskForceMembership.objects.select_related("task_force"):
        membership.joined_at = membership.created_at
        membership.save(update_fields=["joined_at"])
        tf = ProjectTaskForce.objects.get(pk=membership.task_force_id)
        if (membership.role or "").lower() == "leader" and not tf.leader_id:
            tf.leader_id = membership.user_id
            tf.save(update_fields=["leader"])

    by_project = defaultdict(list)
    for tf in ProjectTaskForce.objects.exclude(project_id__isnull=True).order_by("pk"):
        by_project[tf.project_id].append(tf)
    for groups in by_project.values():
        keep, extras = groups[0], groups[1:]
        for extra in extras:
            for membership in TaskForceMembership.objects.filter(task_force=extra):
                if not TaskForceMembership.objects.filter(
                    task_force=keep, user_id=membership.user_id
                ).exists():
                    TaskForceMembership.objects.create(
                        task_force=keep,
                        user_id=membership.user_id,
                        role=membership.role,
                        joined_at=membership.created_at,
                    )
            if extra.leader_id and not keep.leader_id:
                keep.leader_id = extra.leader_id
                keep.save(update_fields=["leader"])
            elif extra.leader_id and extra.leader_id != keep.leader_id:
                if not TaskForceMembership.objects.filter(
                    task_force=keep, user_id=extra.leader_id
                ).exists():
                    TaskForceMembership.objects.create(
                        task_force=keep, user_id=extra.leader_id, role="member"
                    )
            extra.project_id = None
            extra.is_active = False
            extra.save(update_fields=["project_id", "is_active"])


def _system_roles(apps):
    from apps.administration.rbac import ensure_system_roles

    Organization = apps.get_model("administration", "Organization")
    Role = apps.get_model("administration", "Role")
    User = apps.get_model("administration", "User")
    for org in Organization.objects.all():
        ensure_system_roles(org, Role)
    for user in User.objects.filter(role__isnull=True, organization__isnull=False):
        guest = Role.objects.filter(
            organization=user.organization, code="GUEST"
        ).first()
        if guest is not None:
            user.role = guest
            user.save(update_fields=["role"])


def _check_emails(User):
    counts = defaultdict(list)
    for user in User.objects.exclude(email=""):
        counts[user.email].append(user.username)
    duplicates = {email: names for email, names in counts.items() if len(names) > 1}
    if duplicates:
        raise RuntimeError(
            "User e-mail addresses must be unique (SPECIFICATION §15.2.3). "
            f"Fix these duplicates and re-run the migration: {duplicates}"
        )


def forwards(apps, schema_editor):
    _unique_slugs(apps.get_model("administration", "Organization"))
    _task_forces(
        apps.get_model("administration", "ProjectTaskForce"),
        apps.get_model("administration", "TaskForceMembership"),
    )
    _system_roles(apps)
    _check_emails(apps.get_model("administration", "User"))


class Migration(migrations.Migration):
    dependencies = [
        ("administration", "0006_spec_alignment_fields"),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
