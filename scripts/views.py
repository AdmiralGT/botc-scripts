"""
Views module for scripts app.

This module re-exports all views from the modular view files.
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
]
