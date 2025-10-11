from django.db import connection

# Returns a dictionary with character IDs as keys and the number of scripts containing that character as the value
# Characters which are not present in any scripts will not be in the result
def get_all_script_character_counts(queryset):
    with connection.cursor() as cursor:
        cursor.execute(f"""
            SELECT character_instance->>'id' AS character, COUNT(1) AS count
            FROM "scripts_scriptversion"
            CROSS JOIN LATERAL jsonb_array_elements(content) character_instance
            WHERE character_instance->>'id' != '_meta'
            AND scripts_scriptversion.id IN ({queryset.values('id').query})
            GROUP BY character_instance->>'id'
            ORDER BY count DESC
        """)
        return dict(cursor.fetchall())
