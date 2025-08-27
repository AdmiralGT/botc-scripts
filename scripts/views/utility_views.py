"""
Utility views.
"""
import logging

from django.contrib.auth.mixins import UserPassesTestMixin
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.views import generic

from scripts import models, forms, script_json

logger = logging.getLogger(__name__)


class HealthCheckView(generic.View):
    """Simple health check endpoint."""
    
    def get(self, request, *args, **kwargs):
        """Return 200 OK for health checks."""
        return HttpResponse("OK", content_type="text/plain")


class UpdateDatabaseView(UserPassesTestMixin, generic.FormView):
    """View for staff to update scripts in the database."""
    
    template_name = "update_database.html"
    form_class = forms.UpdateDatabaseForm
    success_url = "/update"
    
    def test_func(self):
        """Only staff users can access this view."""
        return self.request.user.is_staff
    
    def handle_no_permission(self):
        """Redirect non-staff users."""
        return redirect("/")
    
    @transaction.atomic
    def form_valid(self, form):
        """Process database update."""
        if not self.request.user.is_staff:
            logger.warning(
                f"Non-staff user {self.request.user.id} attempted database update"
            )
            return redirect("/")
            
        start = form.cleaned_data.get("start", 0)
        end = form.cleaned_data.get("end", 0)
        
        updated_count = 0
        error_count = 0
        
        for i in range(start, end + 1):
            try:
                script_version = models.ScriptVersion.objects.get(pk=i)
                
                # Strip special characters from JSON
                original_content = script_version.content.copy()
                cleaned_content = script_json.strip_special_characters_from_json(
                    script_version.content
                )
                
                # Only save if content actually changed
                if original_content != cleaned_content:
                    script_version.content = cleaned_content
                    script_version.save(update_fields=["content"])
                    updated_count += 1
                    
            except models.ScriptVersion.DoesNotExist:
                # Expected for gaps in PKs
                continue
            except Exception as e:
                logger.error(f"Error updating script version {i}: {e}")
                error_count += 1
                
        # Log the update
        logger.info(
            f"Database update by {self.request.user.username}: "
            f"Range {start}-{end}, Updated: {updated_count}, Errors: {error_count}"
        )
        
        # Add success message
        from django.contrib import messages
        messages.success(
            self.request,
            f"Updated {updated_count} scripts. Errors: {error_count}"
        )
        
        return HttpResponseRedirect(self.get_success_url())
