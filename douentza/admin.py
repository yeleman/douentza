#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import crypt

from django.contrib import admin
from django.conf import settings
from django.contrib.auth.admin import UserAdmin
from django import forms

from douentza.models import (HotlineRequest, HotlineUser,
                             Entity, Survey, Question, QuestionChoice,
                             Ethnicity, CallbackAttempt, Tag, Project,
                             AdditionalRequest, SurveyTaken, SurveyTakenData,
                             BlacklistedNumber, CachedData)


class UserModificationForm(forms.ModelForm):
    class Meta:
        model = HotlineUser


class UserCreationForm(forms.ModelForm):
    class Meta:
        model = HotlineUser
        fields = ('email',)

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()

        def existing_users(filename):
            users = {}
            for userline in open(settings.AUTH_HTTPPASSWD_FILE, 'r').readlines():
                username, passwd = userline.split(':', 1)
                users.update({username: passwd})
            return users

        if settings.AUTH_HTTPPASSWD_FILE is None:
            return user

        try:
            users = existing_users()
        except:
            users = {}

        gen_userline = lambda u, passwd: "{username}:{passwd}\n".format(
            username=u.username,
            passwd=crypt.crypt(passwd))

        with open(settings.AUTH_HTTPPASSWD_FILE, 'w') as f:
            for auser in HotlineUser.objects.all():
                if auser.username in users.keys() and auser.username != user.username:
                    f.write(gen_userline(auser, users.get(auser.username)))
            f.write(gen_userline(user, self.cleaned_data["password"]))
        return user


class CustomUserAdmin(UserAdmin):
    form = UserModificationForm
    add_form = UserCreationForm
    list_display = ("username", "first_name", "last_name")
    ordering = ("username",)

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password', 'first_name',
                           'last_name', 'is_superuser', 'is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password', 'first_name', 'last_name',
                       'is_superuser', 'is_staff', 'is_active')}),
    )


class CustomHotlineRequest(admin.ModelAdmin):
    list_display = ("received_on", "operator", "identity", "event_type",
                    "sms_message", "created_on", "hotline_user",
                    "status", "project")
    list_filter = ("created_on", "event_type", "operator", "hotline_user")


class CustomEntity(admin.ModelAdmin):
    list_display = ("slug", "name", "entity_type", "latitude",
                    "longitude", "parent",)
    list_filter = ("parent", )


class CustomEthnicity(admin.ModelAdmin):
    list_display = ("slug", "name")
    exclude = ("slug",)


admin.site.register(HotlineRequest, CustomHotlineRequest)
admin.site.register(Entity, CustomEntity)
admin.site.register(Survey)
admin.site.register(Question)
admin.site.register(QuestionChoice)
admin.site.register(Ethnicity, CustomEthnicity)
admin.site.register(HotlineUser, CustomUserAdmin)
admin.site.register(CallbackAttempt)
admin.site.register(Project)
admin.site.register(Tag)
admin.site.register(AdditionalRequest)
admin.site.register(SurveyTaken)
admin.site.register(SurveyTakenData)
admin.site.register(BlacklistedNumber)
admin.site.register(CachedData)
