from constants import WILDCARD_DESCRIPTION

NOTHING = object()

WILDCARD_FUNCTION = lambda *args, **kwargs: None
WILDCARD_FUNCTION.__name__ = WILDCARD_DESCRIPTION
