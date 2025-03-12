from django.shortcuts import render
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth import get_user_model

from smtps.models import SmtpManager
from rest_framework.response import Response

from rest_framework.decorators import api_view, permission_classes, authentication_classes

from smtps.serializers import SmtpManagerSerializer

User = get_user_model()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def add_smtp_view(request):
    payload = {}
    errors = {}
    data = {}

    # Get data from the request
    user_id = request.data.get('user_id', "")
    host = request.data.get('host', "")
    port = request.data.get('port', "")
    username = request.data.get('username', "")
    password = request.data.get('password', "")
    ssl = request.data.get('ssl',)

    # Validate input data
    if not user_id:
        errors['user_id'] = ['User ID is required.']
    
    if not host:
        errors['host'] = ['Host is required.']
    
    if not port:
        errors['port'] = ['Port is required.']

    if not username:
        errors['username'] = ['Username is required.']
    if not password:
        errors['password'] = ['Password is required.']

    # Return error response if validation fails
    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        errors['user_id'] = ['User does not exist.']
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)
    
    new_smtp = SmtpManager.objects.create(
        user=user,
        host=host,
        port=port,
        username=username,
        password=password,
        ssl=True
    )



    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_201_CREATED)
    




@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_smtps_view(request):
    payload = {}
    data = {}
    errors = {}

    user_id = request.query_params.get('user_id', None)


    
    if not user_id:
        errors['user_id'] = ['User ID is required.']

    try:
        user = User.objects.get(user_id=user_id)
    except:
        errors['user_id'] = ['User does not exist.']

    
    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)
    

    smtps = SmtpManager.objects.all().filter(is_archived=False, user=user).order_by('-id')
    smtps_serializer = SmtpManagerSerializer(smtps, many=True)


    data['smtps'] = smtps_serializer.data



    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)





@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def delete_smtp(request):
    payload = {}
    errors = {}
    data = {}

    # Get data from the request
    user_id = request.data.get('user_id', "")
    id = request.data.get('id', "")

    print(user_id)
    print(id)

    # Validate input data
    if not user_id:
        errors['user_id'] = ['User ID is required.']

    if not id:
        errors['id'] = ['ID is required.']

    # Return error response if validation fails
    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        errors['user_id'] = ['User does not exist.']
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)
    
    smtp = SmtpManager.objects.get(
        user=user,
        id=id
    )


    smtp.delete()


    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)
    
