from django import forms 
from . models import ReviewRating,Product, Variation


class ReviewForm(forms.ModelForm):
    class Meta:
        model=ReviewRating
        fields=['subject','review','rating']
        
        

