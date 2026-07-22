"""Utility functions."""
import re
from unidecode import unidecode


def generate_slug(text, counter=0):
    """Generate a URL-friendly slug from text.

    If counter > 0, append it to ensure uniqueness.
    """
    slug = unidecode(text.lower())
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s]+', '-', slug)
    slug = slug.strip('-')
    if counter:
        slug = f'{slug}-{counter}'
    return slug
