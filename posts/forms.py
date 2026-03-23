from django import forms
from .models import Post, Comment, Tag


class PostForm(forms.ModelForm):
    tag_input = forms.CharField(
        max_length=200,
        required=False,
        label='Tags',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'sunset, travel, photography (comma separated)',
        })
    )

    class Meta:
        model = Post
        fields = ['image', 'description', 'location', 'category']
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-input',
                'placeholder': 'Write a caption...',
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Add location...',
            }),
            'category': forms.Select(attrs={'class': 'form-input'}),
        }

    def save(self, commit=True):
        post = super().save(commit=commit)
        if commit:
            tag_input = self.cleaned_data.get('tag_input', '')
            post.tags.clear()
            if tag_input:
                tag_names = [t.strip().lower() for t in tag_input.split(',') if t.strip()]
                for name in tag_names:
                    tag, _ = Tag.objects.get_or_create(name=name)
                    post.tags.add(tag)
        return post

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        super().__init__(*args, **kwargs)
        if instance and instance.pk:
            self.fields['tag_input'].initial = ', '.join(
                tag.name for tag in instance.tags.all()
            )


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'content': forms.TextInput(attrs={
                'class': 'comment-input',
                'placeholder': 'Add a comment...',
            })
        }
        labels = {'content': ''}
