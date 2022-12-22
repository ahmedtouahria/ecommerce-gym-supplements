import json
from oauth2client.service_account import ServiceAccountCredentials
from constance import config
from django import template


register = template.Library()
@register.inclusion_tag('admin/analytics.html', takes_context=True)
def analytics(context, next = None):
    ANALYTICS_CREDENTIALS_JSON = config.Google_analytics_credentials
    if type(ANALYTICS_CREDENTIALS_JSON) == dict:
        ANALYTICS_VIEW_ID = config.Google_analytics_id
            # The scope for the OAuth2 request.
        SCOPE = 'https://www.googleapis.com/auth/analytics.readonly'
            # Construct a credentials objects from the key data and OAuth2 scope.
        _credentials = ServiceAccountCredentials.from_json_keyfile_dict(ANALYTICS_CREDENTIALS_JSON, SCOPE)

        return {
            'token': _credentials.get_access_token().access_token,
            'view_id': ANALYTICS_VIEW_ID
        }
    else:
        return {
        'message': 'Veuillez configurer Google analytics pour voir le dashboard'
        }
