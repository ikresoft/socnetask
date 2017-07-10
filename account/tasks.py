# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.contrib.auth import get_user_model
from django.conf import settings
import clearbit


clearbit.key = settings.CLEARBIT_API_KEY
User = get_user_model()


@shared_task
def enrichment(user_id):
    """ get enrichment from clearbit """
    user = User.objects.get(pk=user_id)
    lookup = clearbit.Enrichment.find(email=user.email, stream=True)
    if lookup and ('person' in lookup) and ('name' in lookup['person']):
        user.first_name = lookup['person']['name']['givenName']
        user.last_name = lookup['person']['name']['familyName']
        user.save(update_fields=['first_name', 'last_name'])
    # if no data from enrichment I think it will be good idea
    # to send email to user with link to fullfill data
    return user
