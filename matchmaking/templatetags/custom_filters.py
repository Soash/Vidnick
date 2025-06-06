from django import template
from decimal import Decimal
from users.models import TeacherExpertise

register = template.Library()


@register.simple_tag(name='teacher_rate')
def teacher_rate(expertise_name, class_level_name, user):
    try:
        # Query for the TeacherExpertise model for the logged-in teacher (user), expertise, and class level
        expertise = TeacherExpertise.objects.filter(
            teacher__user=user,  # filter by the logged-in teacher
            expertise_name=expertise_name,  # filter by expertise name
            class_level_name=class_level_name  # filter by class level name
        ).first()
        
        # Return the rate if found, otherwise return "N/A"
        if expertise:
            return expertise.rate
        else:
            return "N/A"
    except TeacherExpertise.DoesNotExist:
        return "N/A"
    

# @register.filter
# def get_rate_by_class(teacher, class_field):
    # """
    # Returns the rate for the given teacher and class_field.
    # """
    # try:
        # expertise = AcademicExpertise.objects.get(teacher=teacher, class_level=class_field)
        # return expertise.rate
    # except AcademicExpertise.DoesNotExist:
        # return "N/A"



# @register.filter
# def get_rate_by_skill(teacher, skill):
#     try:
#         expertise = SkillExpertise.objects.get(teacher=teacher, skill_name=skill)
#         return expertise.rate
#     except SkillExpertise.DoesNotExist:
#         return "N/A"





# @register.simple_tag
# def my_custom_tag_1(teacher, class_level, duration):
#     try:
#         expertise = AcademicExpertise.objects.get(teacher=teacher, class_level=class_level)
#         hourly_rate = Decimal(expertise.rate)  # Ensure rate is a Decimal
#         rate = (Decimal(duration) / Decimal(60)) * hourly_rate  # Convert duration to Decimal
#         return round(rate, 2)
#     except AcademicExpertise.DoesNotExist:
#         return "N/A"

# @register.simple_tag
# def my_custom_tag_2(teacher, skill, duration):
#     try:
#         expertise = SkillExpertise.objects.get(teacher=teacher, skill_name=skill)
#         hourly_rate = Decimal(expertise.rate)  # Ensure rate is a Decimal
#         rate = (Decimal(duration) / Decimal(60)) * hourly_rate  # Convert duration to Decimal
#         return round(rate, 2)
#     except SkillExpertise.DoesNotExist:
#         return "N/A"

    