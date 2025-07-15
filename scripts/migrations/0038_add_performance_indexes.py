# Generated manually for performance optimization

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('scripts', '0037_remove_favourite_script_remove_vote_script'),
    ]

    operations = [
        # Add indexes to ScriptVersion model
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scriptversion_latest ON scripts_scriptversion(latest);",
            reverse_sql="DROP INDEX IF EXISTS idx_scriptversion_latest;"
        ),
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scriptversion_homebrewiness ON scripts_scriptversion(homebrewiness);",
            reverse_sql="DROP INDEX IF EXISTS idx_scriptversion_homebrewiness;"
        ),
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scriptversion_edition ON scripts_scriptversion(edition);",
            reverse_sql="DROP INDEX IF EXISTS idx_scriptversion_edition;"
        ),
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scriptversion_script_type ON scripts_scriptversion(script_type);",
            reverse_sql="DROP INDEX IF EXISTS idx_scriptversion_script_type;"
        ),
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scriptversion_num_demons ON scripts_scriptversion(num_demons);",
            reverse_sql="DROP INDEX IF EXISTS idx_scriptversion_num_demons;"
        ),
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scriptversion_created_desc ON scripts_scriptversion(created DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_scriptversion_created_desc;"
        ),
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scriptversion_pk_desc ON scripts_scriptversion(id DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_scriptversion_pk_desc;"
        ),
        
        # Composite indexes for common combinations
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scriptversion_latest_homebrew ON scripts_scriptversion(latest, homebrewiness);",
            reverse_sql="DROP INDEX IF EXISTS idx_scriptversion_latest_homebrew;"
        ),
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scriptversion_latest_edition ON scripts_scriptversion(latest, edition);",
            reverse_sql="DROP INDEX IF EXISTS idx_scriptversion_latest_edition;"
        ),
        
        # Foreign key indexes
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scriptversion_script_id ON scripts_scriptversion(script_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_scriptversion_script_id;"
        ),
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_script_owner_id ON scripts_script(owner_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_script_owner_id;"
        ),
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_script_name ON scripts_script(name);",
            reverse_sql="DROP INDEX IF EXISTS idx_script_name;"
        ),
        
        # Relationship indexes for stats
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_vote_parent_id ON scripts_vote(parent_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_vote_parent_id;"
        ),
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_vote_user_id ON scripts_vote(user_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_vote_user_id;"
        ),
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_favourite_parent_id ON scripts_favourite(parent_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_favourite_parent_id;"
        ),
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_favourite_user_id ON scripts_favourite(user_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_favourite_user_id;"
        ),
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_comment_script_id ON scripts_comment(script_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_comment_script_id;"
        ),
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_comment_user_id ON scripts_comment(user_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_comment_user_id;"
        ),
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_comment_parent_id ON scripts_comment(parent_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_comment_parent_id;"
        ),
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_comment_created ON scripts_comment(created);",
            reverse_sql="DROP INDEX IF EXISTS idx_comment_created;"
        ),
        
        # Collection indexes
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_collection_owner_id ON scripts_collection(owner_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_collection_owner_id;"
        ),
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_collection_name ON scripts_collection(name);",
            reverse_sql="DROP INDEX IF EXISTS idx_collection_name;"
        ),
        
        # GIN index for JSON content searches (PostgreSQL specific)
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scriptversion_content_gin ON scripts_scriptversion USING GIN(content);",
            reverse_sql="DROP INDEX IF EXISTS idx_scriptversion_content_gin;"
        ),
    ]
