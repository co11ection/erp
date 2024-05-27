from rest_framework.permissions import BasePermission


class CustomPermission(BasePermission):
    def __init__(self, allowed_roles):
        self.allowed_roles = allowed_roles

    def has_permission(self, request, view):
        user = request.user
        if user.role:
            return user.role in self.allowed_roles
        return False


class CanViewGoal(CustomPermission):
    def __init__(self):
        super().__init__(["owner", "admin", "user"])


class CanCreateGoal(CustomPermission):
    def __init__(self):
        super().__init__(["owner", "admin"])


class CanEditGoal(CustomPermission):
    def __init__(self):
        super().__init__(["owner", "admin"])


class CanDeleteGoal(CustomPermission):
    def __init__(self):
        super().__init__(["owner", "admin"])


class CanViewMetric(CustomPermission):
    def __init__(self):
        super().__init__(["owner", "admin", "user"])


class CanCreateMetric(CustomPermission):
    def __init__(self):
        super().__init__(["owner", "admin"])


class CanEditMetric(CustomPermission):
    def __init__(self):
        super().__init__(["owner", "admin"])


class CanDeleteMetric(CustomPermission):
    def __init__(self):
        super().__init__(["owner", "admin"])


class CanViewNews(CustomPermission):
    def __init__(self):
        super().__init__(["owner", "admin", "user"])


class CanCreateEditDeleteNews(CustomPermission):
    def __init__(self):
        super().__init__(["owner", "admin"])


class CanReactToNews(CustomPermission):
    def __init__(self):
        super().__init__(["owner", "admin", "user"])


class CanSendNewsToEmployees(CustomPermission):
    def __init__(self):
        super().__init__(["owner"])


class CanViewUserProfile(CustomPermission):
    def __init__(self):
        super().__init__(["owner", "admin", "user"])


class CanEditUserProfile(CustomPermission):
    def __init__(self):
        super().__init__(["owner"])


class CanChangePasswordUserProfile(CustomPermission):
    def __init__(self):
        super().__init__(["owner", "admin", "user"])


class CanViewReports(CustomPermission):
    def __init__(self):
        super().__init__(["owner", "admin", "user"])


class CanFillReport(CustomPermission):
    def __init__(self):
        super().__init__(["owner", "admin", "user"])


class CanEditReport(CustomPermission):
    def __init__(self):
        super().__init__(["owner", "admin", "user"])


class CanApproveReport(CustomPermission):
    def __init__(self):
        super().__init__(["owner", "admin"])


class CanViewWorkSchedule(CustomPermission):
    def __init__(self):
        super().__init__(["owner", "admin", "user"])


class CanCreateWorkSchedule(CustomPermission):
    def __init__(self):
        super().__init__(["owner", "admin"])


class CanEditWorkSchedule(CustomPermission):
    def __init__(self):
        super().__init__(["owner", "admin"])


class CanViewGeneralResults(CustomPermission):
    def __init__(self):
        super().__init__(["owner", "admin", "user"])


class CanViewResultsForPeriod(CustomPermission):
    def __init__(self):
        super().__init__(["owner", "admin", "user"])


class IsAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.user


class CanAccessUsersAndRoles(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user.users_and_roles_permission


class CanAccessCategoryMetrics(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user.category_metrics_permission


class CanAccessMetrics(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user.metrics_permission


class CanAccessPeriod(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user.period_permission


class CanAccessStatistics(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user.statistick_permission


class CanAccessReports(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user.reports_permission


class CanCreateReports(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user.create_reports_permission
