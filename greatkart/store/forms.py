from django import forms 
from . models import ReviewRating,Product, Variation, VariantImage


class ReviewForm(forms.ModelForm):
    class Meta:
        model=ReviewRating
        fields=['subject','review','rating']
        
        

class ImageForm(forms.ModelForm):
    class Meta:
        model = VariantImage
        fields = ('image',)