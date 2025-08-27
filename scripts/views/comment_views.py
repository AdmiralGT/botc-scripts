"""
Comment-related views.
"""
import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.views import generic

from scripts import models

logger = logging.getLogger(__name__)


class CommentCreateView(LoginRequiredMixin, generic.View):
    """View for creating comments on scripts."""
    
    def post(self, request, *args, **kwargs):
        """Create a new comment."""
        script_id = request.POST.get("script")
        if not script_id:
            logger.warning("Comment creation attempted without script ID")
            return HttpResponseRedirect("/")
            
        script = get_object_or_404(models.Script, pk=script_id)
        redirect_url = f"/script/{script.pk}"
        
        # Get parent comment if this is a reply
        parent = None
        parent_id = request.POST.get("parent")
        if parent_id:
            parent = get_object_or_404(models.Comment, pk=parent_id)
            
        # Create comment if content provided
        comment_text = request.POST.get("comment", "").strip()
        if comment_text:
            models.Comment.objects.create(
                user=request.user,
                comment=comment_text,
                script=script,
                parent=parent
            )
            messages.success(request, "comments-tab")
        else:
            messages.warning(request, "Comment cannot be empty")
            
        return HttpResponseRedirect(redirect_url)


class CommentEditView(LoginRequiredMixin, generic.View):
    """View for editing comments."""
    
    def post(self, request, *args, **kwargs):
        """Edit an existing comment."""
        comment_id = kwargs.get("pk")
        if not comment_id:
            raise Http404("Comment ID required")
            
        comment = get_object_or_404(models.Comment, pk=comment_id)
        
        # Check ownership
        if comment.user != request.user:
            raise Http404("Cannot edit a comment you did not create.")
            
        # Update comment if new content provided
        comment_text = request.POST.get("comment", "").strip()
        if comment_text:
            comment.comment = comment_text
            comment.save()
            messages.success(request, "comments-tab")
        else:
            messages.warning(request, "Comment cannot be empty")
            
        return HttpResponseRedirect(f"/script/{comment.script.pk}")


class CommentDeleteView(LoginRequiredMixin, generic.View):
    """View for deleting comments."""
    
    def post(self, request, *args, **kwargs):
        """Delete a comment."""
        comment_id = kwargs.get("pk")
        if not comment_id:
            raise Http404("Comment ID required")
            
        comment = get_object_or_404(models.Comment, pk=comment_id)
        
        # Check ownership
        if comment.user != request.user:
            raise Http404("Cannot delete a comment you did not make.")
            
        # Re-parent children comments
        if comment.parent:
            for child in comment.children.all():
                child.parent = comment.parent
                child.save()
                
        script_pk = comment.script.pk
        comment.delete()
        
        messages.success(request, "comments-tab")
        return HttpResponseRedirect(f"/script/{script_pk}")
