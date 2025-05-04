from django import template
from django.template import Node

register = template.Library()

class BreakNode(Node):
    def render(self, context):
        raise StopIteration

@register.tag
def break_tag(parser, token):
    """
    Usage: {% break %}
    Breaks out of a loop.
    """
    return BreakNode()

# Register the tag with a name that can be used in templates
register.tag('break', break_tag) 