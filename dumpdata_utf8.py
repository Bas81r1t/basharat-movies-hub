# dumpdata_utf8.py
import json
from django.core.management import call_command
from django.conf import settings

# Ensure settings are configured
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'basharat.settings')

from django import setup
setup()

# Dump data
from io import StringIO

out = StringIO()
call_command('dumpdata', '--natural-primary', '--natural-foreign', '--exclude', 'auth.permission', '--exclude', 'contenttypes', stdout=out)
data = out.getvalue()

# Write UTF-8 without BOM
with open('data.json', 'w', encoding='utf-8') as f:
    f.write(data)

print("✅ data.json exported safely (UTF-8 without BOM)")
