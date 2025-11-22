"""
Script de prueba para verificar la configuración del API
"""
from api_config import settings

print("=" * 60)
print("API Configuration Test")
print("=" * 60)
print(f"API Title: {settings.api_title}")
print(f"API Version: {settings.api_version}")
print(f"Host: {settings.host}")
print(f"Port: {settings.port}")
print(f"Environment: {settings.environment}")
print(f"Reload: {settings.reload}")
print(f"Log Level: {settings.log_level}")
print(f"CORS Origins: {settings.cors_origins}")
print("-" * 60)
print("Paths:")
print(f"API Directory: {settings.api_dir}")
print(f"Project Root: {settings.project_root}")
print(f"Data Directory: {settings.data_dir}")
print("-" * 60)
print(f"PDF Password set: {'Yes' if settings.pdf_password else 'No'}")
print("=" * 60)
print("\n✅ Configuration loaded successfully!")
print(f"📁 .env file location: {settings.api_dir / '.env'}")
print(f"🔍 .env exists: {(settings.api_dir / '.env').exists()}")
