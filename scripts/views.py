"""
Views module for scripts app.

This module re-exports all views from the modular view files for backward compatibility.
"""

# Re-export all views from the modular structure
from scripts.views.script_views import (
    ScriptView,
    ScriptUploadView,
    BaseScriptUploadView,
    ScriptDeleteView,
    AllRolesScriptView,
    download_json,
    download_unsupported_json,
    download_pdf,
    download_all_roles_json,
    get_similar_scripts,
)

from scripts.views.list_views import (
    ScriptsListView,
    UserScriptsListView,
    AdvancedSearchView,
    AdvancedSearchResultsView,
)

from scripts.views.user_views import (
    UserDeleteView,
    vote_for_script,
    favourite_script,
)

from scripts.views.collection_views import (
    CollectionScriptListView,
    CollectionListView,
    CollectionCreateView,
    CollectionEditView,
    CollectionDeleteView,
    AddScriptToCollectionView,
    RemoveScriptFromCollectionView,
)

from scripts.views.comment_views import (
    CommentCreateView,
    CommentEditView,
    CommentDeleteView,
)

from scripts.views.statistics_views import StatisticsView

from scripts.views.utility_views import (
    HealthCheckView,
    UpdateDatabaseView,
)

# Legacy function that might be used elsewhere - now deprecated
def get_comment_data(comment, indent):
    """
    DEPRECATED: This function is kept for backward compatibility.
    Use ScriptView._get_comments_tree() instead.
    """
    import warnings
    warnings.warn(
        "get_comment_data is deprecated. Use ScriptView._get_comments_tree() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    data = []
    comment_data = {}
    comment_data["comment"] = comment
    comment_data["indent"] = indent
    data.append(comment_data)
    for child_comment in comment.children.all().order_by("created"):
        data.extend(get_comment_data(child_comment, min(indent + 1, 6)))
    return data


def get_comments(script):
    """
    DEPRECATED: This function is kept for backward compatibility.
    Use ScriptView._get_comments_tree() instead.
    """
    import warnings
    warnings.warn(
        "get_comments is deprecated. Use ScriptView._get_comments_tree() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    comments = []
    for comment in script.comments.filter(parent__isnull=True).order_by("created"):
        comments.extend(get_comment_data(comment, 0))
    return comments


def count_character(script_content, character_type):
    """
    DEPRECATED: This function is kept for backward compatibility.
    Use ScriptService.count_characters_by_type() instead.
    """
    import warnings
    from scripts.services import ScriptService
    
    warnings.warn(
        "count_character is deprecated. Use ScriptService.count_characters_by_type() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    counts = ScriptService.count_characters_by_type(script_content)
    type_mapping = {
        models.CharacterType.TOWNSFOLK: 'townsfolk',
        models.CharacterType.OUTSIDER: 'outsiders',
        models.CharacterType.MINION: 'minions',
        models.CharacterType.DEMON: 'demons',
        models.CharacterType.TRAVELLER: 'travellers',
        models.CharacterType.FABLED: 'fabled',
    }
    
    return counts.get(type_mapping.get(character_type, ''), 0)


def calculate_edition(script_content):
    """
    DEPRECATED: This function is kept for backward compatibility.
    Use ScriptService.calculate_edition() instead.
    """
    import warnings
    from scripts.services import ScriptService
    
    warnings.warn(
        "calculate_edition is deprecated. Use ScriptService.calculate_edition() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    return ScriptService.calculate_edition(script_content)


def get_all_roles(edition):
    """
    DEPRECATED: This function is kept for backward compatibility.
    Use CharacterService.get_all_roles_for_edition() instead.
    """
    import warnings
    from scripts.services import CharacterService
    
    warnings.warn(
        "get_all_roles is deprecated. Use CharacterService.get_all_roles_for_edition() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    return CharacterService.get_all_roles_for_edition(edition)


def get_edition_from_request(request):
    """
    DEPRECATED: This function is kept for backward compatibility.
    """
    import warnings
    warnings.warn(
        "get_edition_from_request is deprecated.",
        DeprecationWarning,
        stacklevel=2
    )
    
    if "selected_edition" in request.GET:
        for possible_edition in models.Edition:
            if possible_edition.label == request.GET.get("selected_edition"):
                return possible_edition
    return models.Edition.ALL


def update_script(script_version, cleaned_data, author, user):
    """
    DEPRECATED: This function is kept for backward compatibility.
    Use ScriptUploadView._update_script_version() instead.
    """
    import warnings
    from scripts.services import ScriptService
    
    warnings.warn(
        "update_script is deprecated. Use ScriptUploadView._update_script_version() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    script_version.script_type = cleaned_data["script_type"]
    script_version.author = author
    if cleaned_data.get("notes", None):
        script_version.notes = cleaned_data["notes"]
    if cleaned_data.get("pdf", None):
        script_version.pdf = cleaned_data["pdf"]

    ScriptService.update_script_tags(
        script_version,
        cleaned_data["tags"],
        user
    )
    script_version.save()


def get_script(request, pk):
    """
    DEPRECATED: This function is kept for backward compatibility.
    """
    import warnings
    from django.shortcuts import get_object_or_404, redirect
    
    warnings.warn(
        "get_script is deprecated. Use get_object_or_404 directly.",
        DeprecationWarning,
        stacklevel=2
    )
    
    try:
        return models.Script.objects.get(pk=pk)
    except models.Script.DoesNotExist:
        return redirect(request.POST["next"])


def update_user_related_script(model, user, script):
    """
    DEPRECATED: This function is kept for backward compatibility.
    """
    import warnings
    warnings.warn(
        "update_user_related_script is deprecated.",
        DeprecationWarning,
        stacklevel=2
    )
    
    if user.is_authenticated:
        if model.objects.filter(user=user, parent=script).exists():
            object = model.objects.get(user=user, parent=script)
            object.delete()
        else:
            model.objects.create(user=user, parent=script)


def map_similar_scripts(data):
    """
    DEPRECATED: This function is kept for backward compatibility.
    """
    import warnings
    warnings.warn(
        "map_similar_scripts is deprecated.",
        DeprecationWarning,
        stacklevel=2
    )
    
    return {
        "value": data[1],
        "name": data[0].script.name,
        "scriptPK": data[0].script.pk,
    }


def translate_character(character_id, language):
    """
    DEPRECATED: This function is kept for backward compatibility.
    Use CharacterService.translate_character() instead.
    """
    import warnings
    from scripts.services import CharacterService
    
    warnings.warn(
        "translate_character is deprecated. Use CharacterService.translate_character() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    return CharacterService.translate_character(character_id, language)


def translate_json_content(json_content, language):
    """
    DEPRECATED: This function is kept for backward compatibility.
    Use CharacterService.translate_script_content() instead.
    """
    import warnings
    from scripts.services import CharacterService
    
    warnings.warn(
        "translate_json_content is deprecated. Use CharacterService.translate_script_content() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    return CharacterService.translate_script_content(json_content, language)


def translate_content(content, request, language):
    """
    DEPRECATED: This function is kept for backward compatibility.
    """
    import warnings
    from scripts.services import CharacterService
    
    warnings.warn(
        "translate_content is deprecated.",
        DeprecationWarning,
        stacklevel=2
    )
    
    if language or request.GET.get("language_select"):
        language = language if language else request.GET.get("language_select")
        return CharacterService.translate_script_content(content, language)
    return content


def json_file_response(name, content):
    """
    DEPRECATED: This function is kept for backward compatibility.
    """
    import warnings
    import json as js
    from tempfile import TemporaryFile
    from django.http import FileResponse
    
    warnings.warn(
        "json_file_response is deprecated.",
        DeprecationWarning,
        stacklevel=2
    )
    
    json = js.JSONEncoder(ensure_ascii=False).encode(content)
    temp_file = TemporaryFile()
    temp_file.write(json.encode("utf-8"))
    temp_file.flush()
    temp_file.seek(0)
    response = FileResponse(temp_file, as_attachment=True, filename=(name + ".json"))
    return response


def get_character_type_from_team(team):
    """
    DEPRECATED: This function is kept for backward compatibility.
    Use ScriptService.get_character_type_from_team() instead.
    """
    import warnings
    from scripts.services import ScriptService
    
    warnings.warn(
        "get_character_type_from_team is deprecated. Use ScriptService.get_character_type_from_team() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    return ScriptService.get_character_type_from_team(team)


def character_missing_from_database(character_id, roles):
    """
    DEPRECATED: This function is kept for backward compatibility.
    Use ScriptService.is_character_official() instead.
    """
    import warnings
    from scripts.services import ScriptService
    
    warnings.warn(
        "character_missing_from_database is deprecated. Use ScriptService.is_character_official() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    return ScriptService.is_character_official(character_id, roles)


def create_characters_and_determine_homebrew_status(script_content, script):
    """
    DEPRECATED: This function is kept for backward compatibility.
    Use ScriptService.create_or_update_homebrew_characters() instead.
    """
    import warnings
    from scripts.services import ScriptService
    
    warnings.warn(
        "create_characters_and_determine_homebrew_status is deprecated. "
        "Use ScriptService.create_or_update_homebrew_characters() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    return ScriptService.create_or_update_homebrew_characters(script_content, script)


# Import models for the deprecated functions
from scripts import models

__all__ = [
    # Script views
    'ScriptView',
    'ScriptUploadView',
    'BaseScriptUploadView',
    'ScriptDeleteView',
    'AllRolesScriptView',
    'download_json',
    'download_unsupported_json',
    'download_pdf',
    'download_all_roles_json',
    'get_similar_scripts',
    
    # List views
    'ScriptsListView',
    'UserScriptsListView',
    'AdvancedSearchView',
    'AdvancedSearchResultsView',
    
    # User views
    'UserDeleteView',
    'vote_for_script',
    'favourite_script',
    
    # Collection views
    'CollectionScriptListView',
    'CollectionListView',
    'CollectionCreateView',
    'CollectionEditView',
    'CollectionDeleteView',
    'AddScriptToCollectionView',
    'RemoveScriptFromCollectionView',
    
    # Comment views
    'CommentCreateView',
    'CommentEditView',
    'CommentDeleteView',
    
    # Statistics views
    'StatisticsView',
    
    # Utility views
    'HealthCheckView',
    'UpdateDatabaseView',
    
    # Deprecated functions (kept for backward compatibility)
    'get_comment_data',
    'get_comments',
    'count_character',
    'calculate_edition',
    'get_all_roles',
    'get_edition_from_request',
    'update_script',
    'get_script',
    'update_user_related_script',
    'map_similar_scripts',
    'translate_character',
    'translate_json_content',
    'translate_content',
    'json_file_response',
    'get_character_type_from_team',
    'character_missing_from_database',
    'create_characters_and_determine_homebrew_status',
]
