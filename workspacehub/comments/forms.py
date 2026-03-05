from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    
    comment = forms.CharField(label=False, widget=forms.Textarea(attrs={'rows': 3,'placeholder': 'Say something about this...'}), required=True)
    
    class Meta:
        model = Comment
        fields = ['comment']
        
    def clean_comment(self):
        comment = self.cleaned_data.get('comment')
        if len(comment.strip()) < 10:
            raise forms.ValidationError("Comment must be at least 10 characters long")
        return comment
        