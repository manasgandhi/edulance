from django import template

register = template.Library()


@register.filter
def has_applied(post, user):
    return post.applicants.filter(id=user.id).exists()
