"""
User-related views.
"""
import logging

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import redirect, get_object_or_404
from django.views import generic

from scripts import models

logger = logging.getLogger(__name__)


class UserDeleteView(LoginRequiredMixin, generic.TemplateView):
    """View for deleting the currently signed-in user account."""
    
    template_name = "account/delete.html"

    def post(self, request):
        """Delete user account."""
        user = request.user
        
        # Log the deletion for audit purposes
        logger.info(f"User {user.username} (ID: {user.id}) initiated account deletion")
        
        # Logout first
        logout(request)
        
        # Delete the user
        user.delete()
        
        return HttpResponseRedirect("/")


@login_required
def vote_for_script(request, pk: int):
    """Toggle vote for a script."""
    if request.method != "POST":
        raise Http404("Method not allowed")
        
    script = get_object_or_404(models.Script, pk=pk)
    
    # Toggle vote
    vote, created = models.Vote.objects.get_or_create(
        user=request.user,
        parent=script
    )
    
    if not created:
        # Vote exists, remove it (toggle off)
        vote.delete()
        logger.info(f"User {request.user.id} removed vote for script {script.id}")
    else:
        logger.info(f"User {request.user.id} voted for script {script.id}")
        
    # Redirect to the next URL or default to script page
    next_url = request.POST.get("next", f"/script/{script.pk}")
    return redirect(next_url)


@login_required
def favourite_script(request, pk: int):
    """Toggle favourite status for a script."""
    if request.method != "POST":
        raise Http404("Method not allowed")
        
    script = get_object_or_404(models.Script, pk=pk)
    
    # Toggle favourite
    favourite, created = models.Favourite.objects.get_or_create(
        user=request.user,
        parent=script
    )
    
    if not created:
        # Favourite exists, remove it (toggle off)
        favourite.delete()
        logger.info(f"User {request.user.id} removed favourite for script {script.id}")
    else:
        logger.info(f"User {request.user.id} favourited script {script.id}")
        
    # Redirect to the next URL or default to script page
    next_url = request.POST.get("next", f"/script/{script.pk}")
    return redirect(next_url)
