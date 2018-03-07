from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.core.mail import send_mail, EmailMultiAlternatives
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string

from .models import MyUser, Profile, Team, Membership

@admin.register(MyUser)
class UserAdmin(DjangoUserAdmin):
    """Define admin model for custom User model with no username field."""

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser','groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

class MembershipInline(admin.TabularInline):
    model = Membership
    fk_name = 'team'

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'display_name', 'email_confirmed','is_subscribed','steam_id','only_team')
    search_fields = ('user__email', 'display_name')
    readonly_fields = ['steam_id', 'only_team']

    def steam_id(self, obj):
        try:
            return obj.user.social_auth.get(provider='steam').uid
        except:
            return None

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'creator', 'steam_id','size','locked')
    search_fields = ('name', 'creator__email')
    readonly_fields = ['steam_id', 'size']
    actions = ['reg_close', 'lock']

    def size(self, obj):
        return obj.size()
    
    inlines = [
        MembershipInline,
    ]
    
    def steam_id(self, obj):
        try:
            return obj.creator.social_auth.get(provider='steam').uid
        except:
            return None
    
    def lock(self, request, queryset):
        for obj in queryset:
            if not obj.locked:
                obj.lock()
            if obj.size() < 5:    
                subject = 'Your team got a default loss in Frag-Fest due to being incomplete.'
                html_message = render_to_string('email/team_removed_html.html', {
                    'team': obj,
                })
                plain_message = render_to_string('email/team_removed_plain.html', {
                    'team': obj,
                })
                for member in obj.memberships.all():
                    user = member.user
                    msg = EmailMultiAlternatives(subject, plain_message, settings.DEFAULT_FROM_EMAIL, [user.email])
                    msg.attach_alternative(html_message, "text/html")
                    msg.send()

    def reg_close(self, request, queryset):
        for obj in queryset:
            user = obj.creator
            if obj.size() >= 5:
                if not obj.locked:
                    obj.lock()
                subject = 'Frag-Fest registrations closed. Your team has now been locked.'
                html_message = render_to_string('email/registration_success_html.html', {
                    'team': obj,
                })
                plain_message = render_to_string('email/registration_success_plain.html', {
                    'team': obj,
                })
            else:
                if obj.locked:
                    obj.unlock()
                subject = 'Alert! Complete your team on Frag-Fest dashboard.'
                html_message = render_to_string('email/registration_fail_html.html', {
                    'team': obj,
                })
                plain_message = render_to_string('email/registration_fail_plain.html', {
                    'team': obj,
                })
            msg = EmailMultiAlternatives(subject, plain_message, settings.DEFAULT_FROM_EMAIL, [user.email])
            msg.attach_alternative(html_message, "text/html")
            msg.send()

    reg_close.short_description = "Close team registrations."
    lock.short_description = "Lock Teams."

admin.site.register(Membership)

