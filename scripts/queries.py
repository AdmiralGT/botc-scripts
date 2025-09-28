from django.db import connection


# Returns a dictionary with character IDs as keys and the number of scriptts containing that character as the value
# Characters which are not present in any scripts will not be in the result
def get_all_script_character_counts():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT character_type->>'id' AS character, COUNT(1) AS count
            FROM "scripts_scriptversion"
            CROSS JOIN LATERAL jsonb_array_elements(content) character_type
            WHERE character_type->>'id' != '_meta'
            GROUP BY character_type->>'id'
            ORDER BY count DESC
        """)
        return dict(cursor.fetchall())
