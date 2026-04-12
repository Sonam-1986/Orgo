from app.core.config import settings
print(f"SUPABASE_URL: {settings.SUPABASE_URL}")
print(f"SUPABASE_KEY exists: {bool(settings.SUPABASE_KEY and settings.SUPABASE_KEY != 'your-anon-or-service-role-key')}")
