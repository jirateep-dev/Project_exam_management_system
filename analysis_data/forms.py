from django import forms
from database_management.models import ScheduleRoom, DateExam

class ScheduleRoomForm(forms.ModelForm):
    class Meta:
        model = ScheduleRoom
        fields = ('date_id', 'room_id', 'time_id', 'proj_id', 'teacher_group', 'semester', )

class DateExamForm(forms.ModelForm):
    class Meta:
        model = DateExam
        fields = ('id', 'date_exam', 'time_period', 'room_id',)