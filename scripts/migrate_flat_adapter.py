"""Migration helper that produces a unified diff to move flat adapter files into adapters/{adapter_id}/

This script DOES NOT modify files. It prints a patch suitable for `git apply` and a migration commit message template.
"""
from __future__ import annotations
import argparse
import os
import json
import textwrap
from typing import List


def propose_move(old_py: str, old_manifest: str, adapter_id: str) -> str:
    new_dir = f"adapters/{adapter_id}"
    new_py = new_dir + "/adapter.py"
    new_manifest = new_dir + "/manifest.json"
    diffs = []
    # Add file header info
    with open(old_py, "r", encoding="utf-8") as f:
        py_content = f.read()
    with open(old_manifest, "r", encoding="utf-8") as f:
        manifest_content = f.read()

    # Create a patch in git format: create new files and delete old ones
    patch = []
    # new adapter.py
    patch.append(f"*** Begin Patch
*** Add File: {new_py}")
    patch.append(py_content)
    patch.append("*** End Patch")
    # new manifest
    patch.append(f"*** Begin Patch
*** Add File: {new_manifest}")
    patch.append(manifest_content)
    patch.append("*** End Patch")
    # delete old files (note: git apply doesn't support deletions in all cases; provide instructions)
    patch_text = "\n\n".join(patch)
    commit_msg = textwrap.dedent(f"""
    chore: migrate {os.path.basename(old_py)} into adapters/{adapter_id}/

    Migration note:
    - original files: {old_py}, {old_manifest}
    - proposed new location: adapters/{adapter_id}/

    Review the patch and apply with:
      git apply /path/to/patch
      git add adapters/{adapter_id}
      git rm {old_py} {old_manifest}
      git commit -m "chore: migrate {os.path.basename(old_py)} into adapters/{adapter_id}/"
    """)
    return patch_text, commit_msg


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--py', required=True, help='Path to flat adapter python file')
    parser.add_argument('--manifest', required=True, help='Path to flat adapter manifest file')
    parser.add_argument('--adapter-id', required=True, help='Target adapter_id to migrate to')
    args = parser.parse_args(argv)

    patch, commit = propose_move(args.py, args.manifest, args.adapter_id)
    print("---PATCH---")
    print(patch)
    print("---COMMIT MESSAGE---")
    print(commit)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
