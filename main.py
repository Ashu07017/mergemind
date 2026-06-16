import os
print("MergeMind triggered!")
print(f"Repo: {os.environ.get('REPO_FULL_NAME', 'not set')}")
print(f"PR:   {os.environ.get('PR_NUMBER', 'not set')}")