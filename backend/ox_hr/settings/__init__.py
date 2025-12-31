"""
Django settings for core project.

This file imports all settings from the different configuration files.
"""

from dotenv import load_dotenv

load_dotenv()

from .base import *
from .apps import *
from .auth import *
from .databases import *
from .caches import *
from .nats import *
from .permissions import *
from .locale import *
from .email import *
from .static import *

from oxutils.logger.settings import *
