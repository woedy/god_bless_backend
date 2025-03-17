# shortener/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404, redirect
from .models import URL
from .serializers import URLSerializer

@api_view(['POST'])
def create_url(request):
    print(request.data)  # Check what data is being received
    serializer = URLSerializer(data=request.data)
    print(serializer)  # Print the serializer instance
    if serializer.is_valid():
        url_instance = serializer.save()
        return Response({'shortened_url': request.build_absolute_uri(f"/api/{url_instance.shortened_url}/")}, status=status.HTTP_201_CREATED)
    print(serializer.errors)  # Print validation errors
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def redirect_url(request, shortened_url):
    url_instance = get_object_or_404(URL, shortened_url=shortened_url)
    return redirect(url_instance.original_url)
