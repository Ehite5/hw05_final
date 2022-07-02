from django.shortcuts import render

STATUS_404 = 404
STATUS_500 = 500
STATUS_403 = 403


def page_not_found(request, exception):
    return render(request, 'core/404.html', {'path': request.path},
                  status=STATUS_404)


def server_error(request):
    return render(request, 'core/500.html', status=STATUS_500)


def permission_denied_view(request, exception):
    return render(request, 'core/403.html', status=STATUS_403)


def csrf_failure(request, reason=''):
    return render(request, 'core/403csrf.html')
