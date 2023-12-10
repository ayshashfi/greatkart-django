from django import forms
from .models import AdminProfile
from accounts.models import Account



class AdminForm(forms.ModelForm):
    class Meta:
        model=Account
        fields=('first_name','last_name','phone_number')
        
    def __init__(self,*args,**kwargs):
        super(AdminForm,self).__init__(*args,**kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class']='form-control'
            

class AdminProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False, error_messages = {'invalid':("Image files only")}, widget=forms.FileInput)
    class Meta:
        model=AdminProfile
        fields=('address_line_1','address_line_2','city','state','country','profile_picture')
        
    def __init__(self,*args,**kwargs):
        super(AdminProfileForm,self).__init__(*args,**kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class']='form-control'