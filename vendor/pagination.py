from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.response import Response



class CombinedPagination(PageNumberPagination, LimitOffsetPagination):
    
    def paginate_queryset(self, queryset, request, view=None):
        if 'page' in request.query_params or ('limit' not in request.query_params and 'offset' not in request.query_params):
            self.pagination_type = 'page_number'
            print(f"Pagination Type: {self.pagination_type}")
            return PageNumberPagination.paginate_queryset(self, queryset, request, view)
        elif 'limit' in request.query_params and 'offset' in request.query_params:
            self.pagination_type = 'limit_offset'
            print(f"Pagination Type: {self.pagination_type}")
            
            # Set attributes required for LimitOffsetPagination
            self.limit = self.get_limit(request)
            self.offset = self.get_offset(request)
            self.count = self.get_count(queryset)
            self.request = request
            return list(queryset[self.offset:self.offset + self.limit])
        else:
            self.pagination_type = None
            print(f"Pagination Type: {self.pagination_type}")
            return None
    
    def get_paginated_response(self, data):
        if self.pagination_type == 'page_number':
            return Response({
                'Links': {
                    'next': self.get_next_link(),
                    'previous': self.get_previous_link(),
                },
                'count': self.page.paginator.count,
                'results': data,
            })
        elif self.pagination_type == 'limit_offset':
            next_offset = self.offset + self.limit
            previous_offset = max(self.offset - self.limit, 0)

            return Response({
                'Links': {
                    'next': self.get_next_link_for_limit_offset(next_offset),
                    'previous': self.get_previous_link_for_limit_offset(previous_offset),
                },
                'count': self.count,
                'results': data,
            })
        else:
            return Response(data)

    def get_next_link_for_limit_offset(self, next_offset):
        if next_offset >= self.count:
            return None
        return self.request.build_absolute_uri(f'?limit={self.limit}&offset={next_offset}')

    def get_previous_link_for_limit_offset(self, previous_offset):
        if self.offset <= 0:
            return None
        return self.request.build_absolute_uri(f'?limit={self.limit}&offset={previous_offset}')
        