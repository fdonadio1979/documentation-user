# Adapted from https://github.com/sphinx-contrib/redirects

import os
import re
from pathlib import Path

from sphinx.builders import html as builders
from sphinx.util import logging as logging

TEMPLATE = '<html><head><meta http-equiv="refresh" content="0; url=%s"/></head></html>'

logger = logging.getLogger(__name__)

def generate_redirects(app):
    path = os.path.join(app.srcdir, app.config.redirects_file)
    if not os.path.exists(path):
        logger.info("Could not find redirects file at '%s'", path)
        return

    source_suffix = next(iter(app.config.source_suffix))

    if not type(app.builder) == builders.StandaloneHTMLBuilder:
        logger.info("Redirects are only supported by the 'html' builder. Skipping...")
        return

    with open(path) as redirects:
        pattern = re.compile(r'^([\w\-./ ]+)(#.*)?$')
        for line in redirects.readlines():
            # Exclude comment or empty lines
            match_result = pattern.search(line)
            if not match_result:
                continue

            # Parse the rule
            redirect = match_result.group(1).rstrip()
            if redirect.count(' ') != 1:
                logger.error("Ignoring malformed redirection: %s", redirect)
                continue
            from_file, to_file = redirect.split()
            logger.debug("Redirecting '%s' to '%s'", from_file, to_file)

            # Prepare source and destination paths
            to_path_prefix = '../' * from_file.count('/')
            from_html_file = from_file.replace(source_suffix, '.html')
            to_html_file = to_path_prefix + to_file.replace(source_suffix, '.html')
            absolute_from_path = Path(app.builder.outdir) / from_html_file

            # Create the redirection
            absolute_from_path.parent.mkdir(parents=True, exist_ok=True)
            absolute_from_path.write_text(TEMPLATE % to_html_file)


def setup(app):
    app.add_config_value('redirects_file', 'redirects', 'env')
    app.connect('builder-inited', generate_redirects)
