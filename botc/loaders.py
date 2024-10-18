from django.conf import settings
from django.template.loader import BaseLoader
from django.template.base import TemplateDoesNotExist
import os


class BaseTemplateOverrideLoader(BaseLoader):
    """
    Load templates from a specified subdirectory in the current app's directory.
    """

    subdir = "templates"

    def load_template_source(self, template_name, template_dirs=None):
        template_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), self.subdir)

        try:
            t = os.path.join(template_dir, template_name)
            with open(t, "rb") as fp:
                return (fp.read().decode(settings.FILE_CHARSET), template_dir)
        except IOError:
            pass
        raise TemplateDoesNotExist(template_name)


class InlineTemplateLoader(BaseTemplateOverrideLoader):
    """
    Override the location of base.html for inline views.
    """

    is_usable = True
    subdir = "templates/inline"
