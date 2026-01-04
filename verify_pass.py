from werkzeug.security import check_password_hash

hash_val = "scrypt:32768:8:1$swHuMNsktZZ93WZu$8624b6fa3196cf97ffcb3661f193e423629ca64ed5174f44e6d0078d8b0c9998c187c086c0113d62c2a648e0f137157328f3c3eac"
dob = "2025-12-08" # YYYY-MM-DD
username = "U03NK24S0026"

candidates = [
    "08122025",      # DDMMYYYY
    "20251208",      # YYYYMMDD
    "08-12-2025",    # DD-MM-YYYY
    "2025-12-08",    # YYYY-MM-DD
    username,        # Username
    "password123",
    "student123",
    "12345678",
    "01012000"       # Default mentioned in my previous thought
]

print(f"Testing candidates for hash starting with {hash_val[:20]}...")
found = False
for p in candidates:
    if check_password_hash(hash_val, p):
        print(f"MATCH FOUND! Password is: {p}")
        found = True
        break
    else:
        print(f"Failed: {p}")

if not found:
    print("No match found in candidates.")
