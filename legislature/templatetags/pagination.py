# Copyright (C) 2012  Michael Mulley (michaelmulley.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# @see https://github.com/rhymeswithcycle/openparliament/blob/master/parliament/core/templatetags/pagination.py
# @see http://djangosnippets.org/snippets/2763/

from django import template

register = template.Library()

LEADING_PAGE_RANGE_DISPLAYED = TRAILING_PAGE_RANGE_DISPLAYED = 8
LEADING_PAGE_RANGE = TRAILING_PAGE_RANGE = 6
NUM_PAGES_OUTSIDE_RANGE = 2
ADJACENT_PAGES = 2


@register.assignment_tag(takes_context=True)
def long_paginator(context):
    '''
    To be used in conjunction with the object_list generic view.

    Adds pagination context variables for use in displaying leading, adjacent and
    trailing page links in addition to those created by the object_list generic
    view.
    '''

    try:
        page_obj = context['page_obj']
    except KeyError:
        page_obj = context['page']
    try:
        paginator = page_obj.paginator
    except AttributeError:
        return ''
    pages = paginator.num_pages
    if pages <= 1:
        return ''
    page = page_obj.number
    in_leading_range = in_trailing_range = False
    pages_outside_leading_range = pages_outside_trailing_range = range(0)
    if pages <= LEADING_PAGE_RANGE_DISPLAYED + NUM_PAGES_OUTSIDE_RANGE + 1:
        in_leading_range = in_trailing_range = True
        page_range = [n for n in range(1, pages + 1)]
    elif page <= LEADING_PAGE_RANGE:
        in_leading_range = True
        page_range = [n for n in range(1, LEADING_PAGE_RANGE_DISPLAYED + 1)]
        pages_outside_leading_range = [n + pages for n in range(0, -NUM_PAGES_OUTSIDE_RANGE, -1)]
    elif page > pages - TRAILING_PAGE_RANGE:
        in_trailing_range = True
        page_range = [n for n in range(pages - TRAILING_PAGE_RANGE_DISPLAYED + 1, pages + 1) if n > 0 and n <= pages]
        pages_outside_trailing_range = [n + 1 for n in range(0, NUM_PAGES_OUTSIDE_RANGE)]
    else:
        page_range = [n for n in range(page - ADJACENT_PAGES, page + ADJACENT_PAGES + 1) if n > 0 and n <= pages]
        pages_outside_leading_range = [n + pages for n in range(0, -NUM_PAGES_OUTSIDE_RANGE, -1)]
        pages_outside_trailing_range = [n + 1 for n in range(0, NUM_PAGES_OUTSIDE_RANGE)]

    # Now try to retain GET params, except for 'page'
    # Add 'django.core.context_processors.request' to settings.TEMPLATE_CONTEXT_PROCESSORS beforehand
    request = context['request']
    params = request.GET.copy()
    if 'page' in params:
        del params['page']
    if 'partial' in params:
        del params['partial']
    get_params = params.urlencode()

    pagination_ctx = {
        'pages': pages,
        'page': page,
        'previous': page_obj.previous_page_number() if page_obj.has_previous() else None,
        'next': page_obj.next_page_number() if page_obj.has_next() else None,
        'has_previous': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
        'page_range': page_range,
        'in_leading_range': in_leading_range,
        'in_trailing_range': in_trailing_range,
        'pages_outside_leading_range': pages_outside_leading_range,
        'pages_outside_trailing_range': pages_outside_trailing_range,
        'get_params': get_params,
    }

    return template.loader.get_template('long_paginator.html').render(template.Context(pagination_ctx))
