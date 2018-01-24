from django.contrib import admin
from .models import Project, ScoreAdvisor, ScorePoster, ScoreProj, Teacher, Room, ScheduleRoom, Major, Settings
from django.contrib.auth.models import User

admin.autodiscover()
# admin.site.unregister(User)
admin.site.register(Project)
admin.site.register(ScoreAdvisor)
admin.site.register(ScorePoster)
admin.site.register(ScoreProj)
admin.site.register(Teacher)
admin.site.register(Major)
admin.site.register(Room)
admin.site.register(ScheduleRoom)
admin.site.register(Settings)
