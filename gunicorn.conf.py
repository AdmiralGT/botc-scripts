"""Gunicorn configuration.

Gunicorn automatically loads this file when it is present in the working
directory, so it applies on Azure App Service without changing the
Oryx-generated startup command.

Note: settings passed on the command line take precedence over this file.
The Oryx default command supplies --bind and --timeout, so those are
intentionally not set here.
"""

import os

# Threads are only used by the gthread worker class. This workload is largely
# I/O bound (Postgres and Azure Blob Storage), so threads add concurrency
# cheaply without the memory cost of extra processes.
worker_class = "gthread"

# Deliberately not derived from multiprocessing.cpu_count(): a container on
# App Service can report the host's CPU count rather than the CPUs the plan
# actually grants, which would over-provision workers and exhaust memory.
# Tuned for a Basic B2 plan (2 vCPU, 3.5 GB RAM); override via app settings.
workers = int(os.environ.get("GUNICORN_WORKERS", "3"))
threads = int(os.environ.get("GUNICORN_THREADS", "2"))

# Recycle workers periodically to bound memory growth. The jitter staggers
# restarts so workers do not all recycle at the same moment.
max_requests = int(os.environ.get("GUNICORN_MAX_REQUESTS", "1000"))
max_requests_jitter = 100

# Log to stdout/stderr so output is captured by App Service log streaming.
accesslog = "-"
errorlog = "-"
access_log_format = (
    '%(h)s - %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" '
    'xff="%({x-forwarded-for}i)s"'
)
