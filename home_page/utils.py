from datetime import datetime, timedelta
from django.db.models import F, Sum, Value, Count
from django.db.models.functions import Round, Concat
from goals.models import Goal
from periods.models import Periods
from reports.models import Reports


def get_data(selected_period):
    """
    Получает данные о метриках и целях для отчета.

    Returns:
        QuerySet: QuerySet с данными о метриках и целях.
    """

    goal_data = (
        Goal.objects.filter(is_active=True, periods=selected_period)
        .values("name", "category__title")
        .annotate(
            total_revenue=Sum("reports__revenue"),
            goal=F("name"),
            metric_name=F("metrics_name"),
            responsible_user=Concat(
                F("responsible_user__first_name"),
                Value(" "),
                F("responsible_user__last_name"),
            ),
            total_number_range_finally=F("number_range_finally"),
            completion_percentage=Round(
                F("total_revenue") / F("total_number_range_finally") * 100, 2
            ),
            weight_metric=Sum("weight"),
            weight_of_perspective=Sum("weight_of_perspective"),
            perspective_completion_percentage=Round(
                F("weight_of_perspective") * 100, 2
            ),
        )
    )

    return goal_data


def compare_completion_percentage(goals_period1, goals_period2):
    """
    Сравнение процентов завершения целей между двумя периодами.

    Параметры:
    - period1 (Periods): Объект первого периода.
    - period2 (Periods): Объект второго периода.

     Возвращает:
    - list: Список словарей, содержащих данные сравнения целей.

    Пример:
    compare_completion_percentage(period1, period2)
    """
            

    data_to_return = []

    for goal1 in goals_period1:
        matching_goal = goals_period2.filter(name=goal1.name).first()

        if matching_goal:
            completion_percentage_period1 = (
                goal1.reports.aggregate(
                    completion_percentage=Sum("revenue")
                    / Sum(F("goal__number_range_finally"))
                    * 100
                )["completion_percentage"]
                or 0
            )

            completion_percentage_period2 = (
                matching_goal.reports.aggregate(
                    completion_percentage=Sum("revenue")
                    / Sum(F("goal__number_range_finally"))
                    * 100
                )["completion_percentage"]
                or 0
            )
            
            
            difference = completion_percentage_period2 - completion_percentage_period1
            # Create a dictionary to store comparison data
            comparison_data = {
                "category": goal1.category.title,
                "goal_name": goal1.name,
                "completion_percentage_period1": completion_percentage_period1,
                "completion_percentage_period2": completion_percentage_period2,
                "difference": difference,
            }

            # Append comparison data to the list
            data_to_return.append(comparison_data)
    
            
    return data_to_return


def get_user_data(user, user_profile):
    goals_data = []

    user_goals = Goal.objects.filter(responsible_user=user)

    today = datetime.today()
    current_day_of_week = today.weekday()
    delta_to_monday = timedelta(days=current_day_of_week)
    start_of_week = today - delta_to_monday
    end_of_week = start_of_week + timedelta(days=6)

    last_period = Periods.objects.latest("end_date")

    reports_current_week = Reports.objects.filter(
        created_date__range=[start_of_week, end_of_week]
    ).count()
    user_reports_this_week = (
        Reports.objects.filter(
            created_date__range=[start_of_week, end_of_week],
            user=user,
        )
        .annotate(total_reports=Count("id"))
        .values("total_reports")
    )
    if user_reports_this_week and reports_current_week and reports_current_week != 0:
        execution_weekly_iteration = round(
            user_reports_this_week[0].get("total_reports", 0)
            / reports_current_week
            * 100,
            2,
        )
    else:
        execution_weekly_iteration = 0

    last_period_revenue = (
        Reports.objects.filter(period=last_period, user=user).aggregate(
            last_period_revenue=Sum("revenue")
        )["last_period_revenue"]
        or 0
    )

    last_period_plan = (
        Goal.objects.filter(periods=last_period, responsible_user=user).aggregate(
            last_period_plan=Sum("number_range_finally")
        )["last_period_plan"]
        or 0
    )

    if last_period_plan is not None and last_period_plan != 0:
        last_period_result = round(last_period_revenue / last_period_plan * 100, 2)
    else:
        last_period_result = 0
    min_result = None
    max_result = None

    total_number_range_finally = (
        Goal.objects.aggregate(total_number_range_finally=Sum("number_range_finally"))[
            "total_number_range_finally"
        ]
        or 0
    )

    total_number_of_revenue = (
        Reports.objects.aggregate(total_number_of_revenue=Sum("revenue"))[
            "total_number_of_revenue"
        ]
        or 0
    )

    if total_number_range_finally is not None and total_number_range_finally != 0:
        overall_result = round(
            (total_number_of_revenue * 100) / total_number_range_finally, 2
        )
    else:
        overall_result = 0

    user_reports_revenue = Reports.objects.filter(user=user).aggregate(
        user_reports_revenue=Sum("revenue")
    )["user_reports_revenue"]
    if user_reports_revenue is not None and user_reports_revenue != 0:
        result_comparison_team = round(
            total_number_of_revenue / user_reports_revenue * 100, 2
        )
    else:
        result_comparison_team = 0
    for goal in user_goals:
        goal_reports = Reports.objects.filter(goal=goal, user=user)

        # Вычисление суммы поля revenue из отчетов, связанных с конкретной целью
        total_revenue = goal_reports.aggregate(total_revenue=Sum("revenue"))[
            "total_revenue"
        ]

        if total_revenue is not None and goal.number_range_finally != 0:
            result = round(total_revenue / goal.number_range_finally * 100, 2)
        else:
            result = 0
        if min_result is None or result < min_result:
            min_result = result
        if max_result is None or result > max_result:
            max_result = result
        goals_data.append(
            {
                "name": goal.name,
                "metrics_name": goal.metrics_name,
                "category": goal.category.title,
                "digit_range": goal.digit_range,
                "plan": goal.number_range_finally,
                "fact": total_revenue,
                "completion_percentage": result,
                "goal_weight": goal.weight,
                "goal_perspective": goal.weight_of_perspective,
                "perspective_completion_percentage": goal.weight_of_perspective * 100,
            }
        )
    general_data = {
        "days_without_skip": user_profile.days_without_skip,
        "execution_weekly_iteration": execution_weekly_iteration,
        "min_result": min_result,
        "max_result": max_result,
        "last_period_result": last_period_result,
        "overall_result": overall_result,
        "result_comparison_team": result_comparison_team,
        "metrics": goals_data,
        "responsible_user": f"{user.first_name} {user.last_name}",
    }
    return general_data



def get_data_user(user, user_profile, selected_period):
    goals_data = []

    user_goals = Goal.objects.filter(responsible_user=user, periods=selected_period)

    today = datetime.today()
    current_day_of_week = today.weekday()
    delta_to_monday = timedelta(days=current_day_of_week)
    start_of_week = today - delta_to_monday
    end_of_week = start_of_week + timedelta(days=6)

    last_period = Periods.objects.latest("end_date")

    reports_current_week = Reports.objects.filter(
        created_date__range=[start_of_week, end_of_week]
    ).count()
    user_reports_this_week = (
        Reports.objects.filter(
            created_date__range=[start_of_week, end_of_week],
            user=user,
        )
        .annotate(total_reports=Count("id"))
        .values("total_reports")
    )
    if user_reports_this_week and reports_current_week and reports_current_week != 0:
        execution_weekly_iteration = round(
            user_reports_this_week[0].get("total_reports", 0)
            / reports_current_week
            * 100,
            2,
        )
    else:
        execution_weekly_iteration = 0

    last_period_revenue = (
        Reports.objects.filter(period=last_period, user=user).aggregate(
            last_period_revenue=Sum("revenue")
        )["last_period_revenue"]
        or 0
    )

    last_period_plan = (
        Goal.objects.filter(periods=last_period, responsible_user=user).aggregate(
            last_period_plan=Sum("number_range_finally")
        )["last_period_plan"]
        or 0
    )

    if last_period_plan is not None and last_period_plan != 0:
        last_period_result = round(last_period_revenue / last_period_plan * 100, 2)
    else:
        last_period_result = 0
    min_result = None
    max_result = None

    total_number_range_finally = (
        Goal.objects.aggregate(total_number_range_finally=Sum("number_range_finally"))[
            "total_number_range_finally"
        ]
        or 0
    )

    total_number_of_revenue = (
        Reports.objects.aggregate(total_number_of_revenue=Sum("revenue"))[
            "total_number_of_revenue"
        ]
        or 0
    )

    if total_number_range_finally is not None and total_number_range_finally != 0:
        overall_result = round(
            (total_number_of_revenue * 100) / total_number_range_finally, 2
        )
    else:
        overall_result = 0

    user_reports_revenue = Reports.objects.filter(user=user).aggregate(
        user_reports_revenue=Sum("revenue")
    )["user_reports_revenue"]
    if user_reports_revenue is not None and user_reports_revenue != 0:
        result_comparison_team = round(
            total_number_of_revenue / user_reports_revenue * 100, 2
        )
    else:
        result_comparison_team = 0
    for goal in user_goals:
        goal_reports = Reports.objects.filter(goal=goal, user=user)

        # Вычисление суммы поля revenue из отчетов, связанных с конкретной целью
        total_revenue = goal_reports.aggregate(total_revenue=Sum("revenue"))[
            "total_revenue"
        ]

        if total_revenue is not None and goal.number_range_finally != 0:
            result = round(total_revenue / goal.number_range_finally * 100, 2)
        else:
            result = 0
        if min_result is None or result < min_result:
            min_result = result
        if max_result is None or result > max_result:
            max_result = result
        goals_data.append(
            {
                "name": goal.name,
                "metrics_name": goal.metrics_name,
                "category": goal.category.title,
                "digit_range": goal.digit_range,
                "plan": goal.number_range_finally,
                "fact": total_revenue,
                "completion_percentage": result,
                "goal_weight": goal.weight,
                "goal_perspective": goal.weight_of_perspective,
                "perspective_completion_percentage": goal.weight_of_perspective * 100 if goal.weight_of_perspective else 0,
            }
        )
    general_data = {
        "days_without_skip": user_profile.days_without_skip,
        "execution_weekly_iteration": execution_weekly_iteration,
        "min_result": min_result,
        "max_result": max_result,
        "last_period_result": last_period_result,
        "overall_result": overall_result,
        "result_comparison_team": result_comparison_team,
        "metrics": goals_data,
        "responsible_user": f"{user.first_name} {user.last_name}",
    }
    return general_data