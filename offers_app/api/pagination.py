from rest_framework.pagination import PageNumberPagination


class OfferPagination(PageNumberPagination):
    """Paginate offers and support a custom page size."""

    page_size = 6
    page_size_query_param = "page_size"
    max_page_size = 100
