from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    # Default page size if not specified in the request
    page_size = 10 
    # Allows clients to override the page size using a 'page_size' query parameter
    page_size_query_param = 'page_size' 
    # Maximum allowed page size
    max_page_size = 100
     