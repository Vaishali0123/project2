from google_auth_oauthlib.flow import Flow
from django.shortcuts import redirect
from django.http import HttpResponse
from rest_framework.views import APIView
from googleapiclient.discovery import build
import datetime

from .settings import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI


class GoogleCalendarInitView(APIView):
    def get(self, request):
        flow = Flow.from_client_secrets_file(
            'path/to/credentials.json',
            scopes=['https://www.googleapis.com/auth/calendar.readonly'],
            redirect_uri=GOOGLE_REDIRECT_URI
        )
        authorization_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        return redirect(authorization_url)


class GoogleCalendarRedirectView(APIView):
    def get(self, request):
        flow = Flow.from_client_secrets_file(
            'path/to/credentials.json',
            scopes=['https://www.googleapis.com/auth/calendar.readonly'],
            redirect_uri=GOOGLE_REDIRECT_URI
        )
        flow.fetch_token(
            authorization_response=request.build_absolute_uri(),
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET
        )
        credentials = flow.credentials
        events = self.fetch_events_from_calendar(credentials)
        # Use the credentials to fetch events from the user's calendar
        # Example:
        # events = self.fetch_events_from_calendar(credentials)

        return HttpResponse("Events fetched successfully.")

    def fetch_events_from_calendar(self, credentials):
        # Create an authorized Google Calendar API client using the credentials
        service = build('calendar', 'v3', credentials=credentials)

        # Set the time range for fetching events (e.g., past week to future week)
        now = datetime.datetime.utcnow()
        week_ago = now - datetime.timedelta(days=7)
        week_later = now + datetime.timedelta(days=7)

        # Fetch events from the user's primary calendar within the time range
        events_result = service.events().list(
            calendarId='primary',
            timeMin=week_ago.isoformat() + 'Z',
            timeMax=week_later.isoformat() + 'Z',
            maxResults=10,  # Number of events to fetch (adjust as needed)
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])
        return events
