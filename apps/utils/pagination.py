from rest_framework import status
from rest_framework.pagination import PageNumberPagination

DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 50


class CustomPaginator(PageNumberPagination):
    page = DEFAULT_PAGE
    page_size = DEFAULT_PAGE_SIZE
    page_size_query_param = "limit"

    def generate_response(self, query_set, serializer_obj, request):
        if request.GET.get("is_paging") == "false":
            page_data = query_set
            serialized_page = serializer_obj(page_data, many=True, context={"request": request})
            response = {
                "status": status.HTTP_200_OK,
                "message": "ok",
                "total": query_set.count(),
                "total_pages": 1,
                "page": int(request.GET.get("page", DEFAULT_PAGE)),
                "limit": query_set.count(),
                "results": serialized_page.data,
            }
        else:
            try:
                page_data = self.paginate_queryset(query_set, request)
            except Exception as ex:
                response = {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "No results found for the requested page",
                }
                return response
            serialized_page = serializer_obj(page_data, many=True, context={"request": request})
            response = {
                "status": status.HTTP_200_OK,
                "message": "ok",
                "total": self.page.paginator.count,
                "total_pages": self.page.paginator.num_pages,
                "page": int(request.GET.get("page", DEFAULT_PAGE)),
                "limit": int(request.GET.get("page_size", self.page_size)),
                "results": serialized_page.data,
            }
        return response
