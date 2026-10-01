from django.contrib import admin
from .models import PartnerRequest, PartnerRequestJoin

admin.site.register([PartnerRequest, PartnerRequestJoin])
