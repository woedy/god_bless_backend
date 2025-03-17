import random
import requests
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.contrib.auth import get_user_model

from django.conf import settings
from rest_framework.authentication import TokenAuthentication

from dashboard.api.serializers import PhoneNumberSerializer
from phone_generator.api.serializers import AllPhoneNumbersSerializer
from phone_generator.models import PhoneNumber
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated

from projects.models import Project
from smtps.models import SmtpManager
from smtps.serializers import SmtpManagerSerializer
### Twilio, NumVerify, or Nexmo , apilayer , phonenumbers
User = get_user_model()





@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def dashboard_view(request):
    payload = {}
    data = {}
    errors = {}

    user_id = request.query_params.get('user_id', None)
    project_id = request.query_params.get('project_id', None)


    
    if not user_id:
        errors['user_id'] = ['User ID is required.']
    
    if not project_id:
        errors['project_id'] = ['Project ID is required.']

    try:
        user = User.objects.get(user_id=user_id)
    except:
        errors['user_id'] = ['User does not exist.']

    try:
        project = Project.objects.get(id=project_id)
    except:
        errors['project_id'] = ['Project does not exist.']

    
    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)
    

    all_numbers = PhoneNumber.objects.all().filter(is_archived=False, project=project, user=user).order_by('-id')
    all_numbers_serializer = PhoneNumberSerializer(all_numbers[:5], many=True)

    valid_numbers = PhoneNumber.objects.all().filter(is_archived=False, valid_number=True, type='Mobile', project=project, user=user).order_by('-id')
    valid_numbers_serializer = PhoneNumberSerializer(valid_numbers[:5], many=True)

    smtps = SmtpManager.objects.all().filter(is_archived=False, user=user).order_by('-id')
    #smtps_serializer = SmtpManagerSerializer(smtps, many=True)

    all_projects = Project.objects.all().filter(is_archived=False, user=user).order_by('-id')

    data['projects_count'] = all_projects.count()
    data['generated_count'] = all_numbers.count()
    data['validated_count'] = valid_numbers.count()
    data['sms_sent_count'] = 0
    data['api_usage_count'] = 0

    data['sent_email'] = 0
    data['sent_sms'] = 0
    data['loaded_smtps'] = smtps.count()
    data['email_templates'] = 0

    data['recent_generated'] = all_numbers_serializer.data
    data['recent_validated'] = valid_numbers_serializer.data



    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)

