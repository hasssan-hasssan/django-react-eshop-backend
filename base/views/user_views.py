from django.db import IntegrityError
import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.conf import settings
from django.http import HttpResponseRedirect
from base.serializers import UserSerializer, UserSerializerWithToken
from base.strConst import (
    NEW_REGISTER, DETAIL,
    IS_NOT_ACTIVE,
    SUCCESS_NEW_REGISTER,
    ERROR_ON_SENDING_EMAIL,
    ERROR_USER_EXISTS_IS_NOT_ACTIVE,
    ERROR_USER_EXISTS_IS_ACTIVE_TOO,
    ERROR_UNEXPECTED
)
from base import utils
import jwt


# Define an API endpoint to retrieve the profile of the authenticated user
@api_view(['GET'])  # Endpoint supports GET requests
@permission_classes([IsAuthenticated])  # Requires user authentication
def getUserProfile(request):
    user = request.user  # Retrieve the authenticated user
    serializer = UserSerializer(user, many=False)  # Serialize the user's data
    # Return the serialized data as a response
    return Response(serializer.data)


# Define an API endpoint to retrieve all registered users (for admin use only)
@api_view(['GET'])  # Endpoint supports GET requests
@permission_classes([IsAdminUser])  # Requires admin-level permissions
def getUsers(request):
    users = User.objects.all()  # Retrieve all users from the database
    # Serialize the list of users
    serializer = UserSerializer(users, many=True)
    # Return the serialized data as a response
    return Response(serializer.data)


@api_view(['POST'])  # Specifies that this view only handles POST requests
def registerUser(request):
    # Extract user registration data from the request body
    data = request.data
    username = data['email']  # Email is used as the username
    password = data['password']  # Password provided by the user

    try:
        # Attempt to create a new user with the provided data
        user = User.objects.create(
            first_name=data['name'],  # First name of the user
            username=data['email'],  # Username is set to the email
            email=data['email'],  # Email address
            # Hash the password for security
            password=make_password(data['password']),
            is_active=False  # Set the user as inactive until email verification
        )

        # Generate an activation link for email verification
        activationLink = utils.createActivationLink(user)
        # Create the email content using the activation link
        email = utils.createEmail(NEW_REGISTER, activationLink, user)

        # Attempt to send the activation email
        if utils.sendEmail(email):
            # If email is successfully sent, return a success response
            return Response({DETAIL: SUCCESS_NEW_REGISTER}, status=status.HTTP_201_CREATED)
        else:
            # If email sending fails, return an internal server error
            return Response({DETAIL: ERROR_ON_SENDING_EMAIL}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except IntegrityError:
        # IntegrityError is triggered when a user with the same email already exists
        # Safely fetch the user (returns None if not found)
        user = User.objects.filter(username=username).first()

        if user and not user.is_active:
            # If the user exists but is inactive, update their password
            # Hash and set the new password
            user.password = make_password(password)
            user.save()  # Save the user object to the database

            # Generate a new activation link and email content
            activationLink = utils.createActivationLink(user)
            email = utils.createEmail(IS_NOT_ACTIVE, activationLink, user)

            # Attempt to resend the activation email
            if utils.sendEmail(email):
                # If email is successfully sent, return a response indicating the user exists but is not active
                return Response({DETAIL: ERROR_USER_EXISTS_IS_NOT_ACTIVE}, status=status.HTTP_200_OK)
            else:
                # If email sending fails, return an internal server error
                return Response({DETAIL: ERROR_ON_SENDING_EMAIL}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        elif user and user.is_active:
            # If the user exists and is already active, notify the client
            return Response({DETAIL: ERROR_USER_EXISTS_IS_ACTIVE_TOO}, status=status.HTTP_200_OK)

        else:
            # If no user is found or some unexpected error occurs, return a generic error response
            return Response({DETAIL: ERROR_UNEXPECTED}, status=status.HTTP_400_BAD_REQUEST)


# Define an API endpoint to update the profile of the authenticated user
@api_view(['PUT'])  # Endpoint supports PUT requests
@permission_classes([IsAuthenticated])  # Requires user authentication
def updateUserProfile(request):
    user = request.user  # Retrieve the authenticated user
    data = request.data  # Extract profile update data from the request body

    # Update user fields with the provided data
    user.first_name = data['name']
    user.email = data['email']
    user.username = data['email']
    if data['password'] != '':  # Update the password if provided
        user.password = make_password(data['password'])
    user.save()  # Save the updated user object

    # Serialize the updated user object with a token
    serializer = UserSerializerWithToken(user, many=False)
    # Return the serialized data as a response
    return Response(serializer.data)


# Define an API endpoint to verify a user's email using a token
@api_view(['GET'])  # Endpoint supports GET requests
def verifyEmail(request, token):
    try:
        # Decode the JWT token to retrieve the user payload
        payload = jwt.decode(
            jwt=token,
            key=settings.SECRET_KEY,
            algorithms=[settings.SIMPLE_JWT['ALGORITHM']]
        )
    except:
        # Redirect to the frontend login page with an invalid token message if decoding fails
        return HttpResponseRedirect(f'{settings.FRONTEND_DOMAIN}/login?token=invalid')
    else:
        # Activate the user if the token is valid
        user = User.objects.get(id=payload['user_id'])
        user.is_active = True
        user.save()
        # Redirect to the frontend login page with a valid token message
        return HttpResponseRedirect(f'{settings.FRONTEND_DOMAIN}/login?token=valid')
