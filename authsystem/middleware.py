from django.utils.deprecation import MiddlewareMixin

class AppendSlashWithoutRedirectMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path.startswith('/api/'):
            if not request.path.endswith('/') and not '?' in request.path:
                path = request.path + '/'
                if request.META.get('QUERY_STRING'):
                    path += '?' + request.META.get('QUERY_STRING')
                
                request.path = path
                request.path_info = path
        
        return None