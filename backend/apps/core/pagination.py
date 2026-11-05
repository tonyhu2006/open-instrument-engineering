from rest_framework.pagination import PageNumberPagination


class StandardPagination(PageNumberPagination):
    """§4.2.1: ``?page=1&page_size=50`` — default 50, max 500."""

    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 500
