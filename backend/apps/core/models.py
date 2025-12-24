"""
Core App Models - Base models and utilities
"""

from django.db import models


class TimeStampedModel(models.Model):
    """
    Abstract base model with created and modified timestamps.
    All other models should inherit from this.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
