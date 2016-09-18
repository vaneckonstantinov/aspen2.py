# for backwards compatibility with aspen-renderer modules
from .simplates.renderers import Factory, Renderer

Factory, Renderer # make pyflakes happy

import warnings
warnings.warn('aspen.renderers is deprecated and will be removed in a future version. '
              'Please use aspen.simplates.renderers instead.', FutureWarning)
