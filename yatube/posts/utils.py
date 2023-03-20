from django.core.paginator import Paginator

POST_PER_PAGE: int = 10


def paginator_page(request, posts):

    paginator = Paginator(posts, POST_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return page_obj
