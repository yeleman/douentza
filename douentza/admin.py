#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms

from douentza.models import (HotlineEvent, HotlineUser,
                             Entity, Survey, Question, QuestionChoice,
                             Ethnicity, CallbackAttempt, Tag, Project)


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
        return user


class CustomUserAdmin(UserAdmin):
    form = UserModificationForm
    add_form = UserCreationForm
    list_display = ("username", "first_name", "last_name", "operator")
    ordering = ("username",)

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password', 'first_name',
                           'last_name', 'is_superuser', 'is_staff', 'is_active',
                           'operator', 'phone_number')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password', 'first_name', 'last_name',
                       'is_superuser', 'is_staff', 'is_active', 'operator')}),
    )


class CustomHotlineEvent(admin.ModelAdmin):
    list_display = ("received_on", "operator", "identity", "event_type",
                    "sms_message", "created_on", "hotline_user",
                    "status")
    list_filter = ("created_on", "event_type", "operator", "hotline_user")


class CustomEntity(admin.ModelAdmin):
    list_display = ("slug", "name", "entity_type", "latitude",
                    "longitude", "parent",)
    list_filter = ("parent", )


class CustomEthnicity(admin.ModelAdmin):
    list_display = ("slug", "name")
    exclude = ("slug",)


admin.site.register(HotlineEvent, CustomHotlineEvent)
admin.site.register(Entity, CustomEntity)
admin.site.register(Survey)
admin.site.register(Question)
admin.site.register(QuestionChoice)
admin.site.register(Ethnicity, CustomEthnicity)
admin.site.register(HotlineUser)
admin.site.register(CallbackAttempt)
admin.site.register(Project)
admin.site.register(Tag)
