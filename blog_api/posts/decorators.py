# import functools

# from rest_framework.response import Response


# def require_request_params(function):
#     """Require params in request. Else return DRF response 400."""
#     @functools.wraps(function)
#     def _inner(request, *args, **kwargs):
#         # if not request.data.keys():
#         #     return Response({
#         #             'message': 'You must include params in the request.'
#         #         }, status=HTTP_400_BAD_REQUEST
#         #     )
#         print(request.META)
#         return function(request, *args, **kwargs)
#     return _inner
