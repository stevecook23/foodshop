from django import forms
from .models import Product, Category, Review

class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = Category.objects.all()
        friendly_names = [(c.id, c.get_friendly_name()) for c in categories]

        self.fields['categories'].choices = friendly_names
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'border-black rounded-0'
            
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['headline', 'review_text']
        widgets = {
            'headline': forms.TextInput(attrs={'class': 'form-control'}),
            'review_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'maxlength': 500}),
        }