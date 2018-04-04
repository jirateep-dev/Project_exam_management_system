from django import forms
from database_management.models import Project, Student

class ProjectForm(forms.ModelForm):
    proj_co_advisor = forms.CharField(max_length=1024, required=False)
    class Meta:
        model = Project
        fields = ('proj_years', 'proj_semester', 'proj_name_th', 'proj_name_en', 'proj_major','proj_advisor', 'proj_co_advisor',)

class StudentForm(forms.ModelForm):
    proj1_id = forms.CharField(max_length=1024, required=False)
    proj2_id = forms.CharField(max_length=1024, required=False)
    class Meta:
        model = Student
        fields = ('proj1_id', 'proj2_id', 'student_id', 'student_name',)