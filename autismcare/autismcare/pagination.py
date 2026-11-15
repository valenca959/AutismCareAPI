from rest_framework.pagination import PageNumberPagination


class PaginacaoPadrao(PageNumberPagination):
    """
    Listagens paginadas: ?page=2 escolhe a página e ?page_size=50 o tamanho (máx. 100).
    Resposta: {"count", "next", "previous", "results"}.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
