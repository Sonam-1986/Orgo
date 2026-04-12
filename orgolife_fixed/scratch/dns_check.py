import socket
host = "db.htcooghlfkazzszfnurw.supabase.co"
try:
    ip = socket.gethostbyname(host)
    print(f"SUCCESS: {host} resolves to {ip}")
except Exception as e:
    print(f"FAILED: {host} does not resolve: {e}")

pooler = "aws-0-ap-south-1.pooler.supabase.com"
try:
    ip = socket.gethostbyname(pooler)
    print(f"POOLER SUCCESS: {pooler} resolves to {ip}")
except Exception as e:
    print(f"POOLER FAILED: {pooler} does not resolve: {e}")
