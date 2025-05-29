from rest_framework.pagination import PageNumberPagination


class UserInfoPagination(PageNumberPagination):
    page_size_query_param = 'limit'
