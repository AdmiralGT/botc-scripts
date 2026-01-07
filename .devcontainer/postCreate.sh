#!/bin/bash
set -e

echo "🚀 Setting up BOTC Scripts development environment..."

# Install Python dependencies
echo "📦 Installing Python dependencies with uv..."
uv sync

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
until pg_isready -h localhost -p 5432 -U "postgres@db" > /dev/null 2>&1; do
  sleep 1
done
echo "✅ PostgreSQL is ready!"

# Create local.py configuration if it doesn't exist
if [ ! -f "botc/local.py" ]; then
  echo "⚙️  Creating botc/local.py configuration..."
  cat > botc/local.py << 'EOF'
from .settings import *

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "postgres",
        "HOST": "localhost",
        "USER": "postgres@db",
        "PASSWORD": "postgres",
    }
}

SECRET_KEY = "dev-secret-key-change-in-production-$(openssl rand -hex 32)"

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
BS_ICONS_CACHE = os.path.join(STATIC_ROOT, "icon_cache")
DEBUG = True

INTERNAL_IPS = [
    "127.0.0.1",
    "localhost",
]
EOF
  echo "✅ Configuration created!"
else
  echo "ℹ️  botc/local.py already exists, skipping..."
fi

# Run migrations
echo "🔄 Running database migrations..."
uv run python manage.py migrate

# Install pg_trgm extension
echo "🔧 Installing PostgreSQL trigram extension..."
PGPASSWORD=postgres psql -h localhost -U "postgres@db" -d postgres -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;" || echo "Extension may already exist"

# Collect static files
echo "📁 Collecting static files..."
uv run python manage.py collectstatic --noinput

# Load character data
echo "🎭 Loading character data..."
uv run python manage.py loaddata dev/characters || echo "Character data may already be loaded"

echo ""
echo "✨ Setup complete! Next steps:"
echo "   1. Create a superuser: uv run python manage.py createsuperuser"
echo "   2. Start the development server: uv run python manage.py runserver"
echo "   3. Visit http://localhost:8000"
echo "   4. Admin panel: http://localhost:8000/admin"
echo ""
