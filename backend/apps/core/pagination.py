"""Pagination standard : { "count", "next", "previous", "results" }."""
from rest_framework.pagination import PageNumberPagination


class PaginationStandard(PageNumberPagination):
    page_size = 50                    
    page_size_query_param = "page_size"
    max_page_size = 100               