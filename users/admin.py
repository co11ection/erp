from django.contrib import admin
from .models import User

# class UserAdmin(admin.ModelAdmin):
#     list_display = (
#         'email', 'first_name', 'last_name')
#     list_filter = ('is_owner', 'is_admin', 'is_employer')
#     search_fields = ('email', 'first_name', 'last_name')
#     readonly_fields = ('activation_code',)
#
#     def get_fieldsets(self, request, obj=None):
#         fieldsets = super().get_fieldsets(request, obj)
#         if not obj:
#             fieldsets = (
#                 (None, {'fields': ('email', 'password')}),
#                 ('Personal Info', {'fields': (
#                     'first_name', 'middle_name', 'last_name', 'date_of_birth', 'telegram', 'phone_number', 'role')}),
#
#             )
#         else:
#             fieldsets = (
#                 (None, {'fields': ('email',)}),
#                 ('Personal Info', {'fields': (
#                     'first_name', 'middle_name', 'last_name', 'date_of_birth', 'telegram', 'phone_number', 'role')}),
#
#             )
#         return fieldsets


admin.site.register(User)
