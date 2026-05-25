import os

print("Checking environment variables:")
for k in os.environ:
    if "SUPABASE" in k or "SECRET" in k or "CONN" in k:
        print(f"{k}: {os.environ[k][:10]}...")
