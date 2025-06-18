from rest_framework import status
from django.db.models import Q
from rest_framework.response import Response


# def list_resources(
#     request,
#     model_class,
#     filter_class,
#     soft_delete=False,
# ):
#     """
#     Generalized function to list resources with filtering, pagination, and optional soft delete handling.
#     Returns a paginated response with serialized data or an error response.
#     """
#     user = request.user
#     queryset = model_class.objects.all()

#     if user.is_staff or user.is_superuser:
#         user_id = request.query_params.get("user")
#         if user_id:
#             queryset = queryset.filter(user_id=user_id)
#     else:
#         if model_class == Category:
#             queryset = queryset.filter(Q(user_id=user) | Q(user_id=None))
#         else:
#             queryset = queryset.filter(user_id=user)

#         if soft_delete:
#             queryset = queryset.filter(is_active=True)

#     # Apply filters
#     filterset = filter_class(request.query_params, queryset=queryset)
#     if not filterset.is_valid():
#         return Response(response, status=status_code)
#         return send_structured_response(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             errors=filterset.errors.as_data(),
#         )

#     return filterset.qs
