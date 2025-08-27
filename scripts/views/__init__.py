"""
Views package for scripts app.
"""
from .script_views import (
    ScriptView,
    ScriptUploadView,
    BaseScriptUploadView,
    ScriptDeleteView,
    AllRolesScriptView,
    download_json,
    download_unsupported_json,
    download_pdf,
    download_all_roles_json,
    get_similar_scripts
)
from .list_views import (
    ScriptsListView,
    UserScriptsListView,
    AdvancedSearchView,
    AdvancedSearchResultsView
)
from .user_views import (
    UserDeleteView,
    vote_for_script,
    favourite_script
)
from .collection_views import (
    CollectionScriptListView,
    CollectionListView,
    CollectionCreateView,
    CollectionEditView,
    CollectionDeleteView,
    AddScriptToCollectionView,
    RemoveScriptFromCollectionView
)
from .comment_views import (
    CommentCreateView,
    CommentEditView,
    CommentDeleteView
)
from .statistics_views import StatisticsView
from .utility_views import (
    HealthCheckView,
    UpdateDatabaseView
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
