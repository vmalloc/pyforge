from .constants import WILDCARD_DESCRIPTION

WILDCARD_FUNCTION = lambda *args, **kwargs: None
WILDCARD_FUNCTION.__name__ = WILDCARD_DESCRIPTION

# unfortunately there doesn't appear to be another way of getting
# this type
MethodDescriptorType = type(dict.get)
