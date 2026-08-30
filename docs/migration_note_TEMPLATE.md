# Migration note template

When migrating a flat adapter file into the adapters/{adapter_id}/ layout, include this note in the commit message or as a companion README in the adapter directory.

- Original files:
  - adapters/weather_example.py
  - adapters/weather_example.manifest.json
- New location:
  - adapters/{adapter_id}/adapter.py
  - adapters/{adapter_id}/manifest.json
- Reason: standardize on per-adapter directories for lifecycle management, tests, and metadata.

Include the original commit SHA(s) that introduced the flat files for traceability.
