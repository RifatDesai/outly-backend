from django.contrib import admin
from .models import Group, GroupMembership, GroupJoinRequest, GroupPost

admin.site.register([Group, GroupMembership, GroupJoinRequest, GroupPost])
