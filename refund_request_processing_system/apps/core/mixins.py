from django import forms
from django.core.cache import cache


class BootstrapFormMixin:
    template_name_div = "forms/bootstrap_div.html"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css_class = 'form-control'
            if isinstance(field.widget, forms.Select):
                css_class = 'form-select'

            current_css_classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = (
                f'{current_css_classes} {css_class}'.strip()
            )


class OnlyOwnedObjectsViewMixin:
    user_field_for_filter = 'user'

    def get_queryset(self):
        qs = super().get_queryset()

        if self.request.user.is_authenticated:
            filter_kwargs = {self.user_field_for_filter: self.request.user}
            return qs.filter(**filter_kwargs)

        return qs.none()


class ClearCacheTestMixin:
    def setUp(self):
        super().setUp()
        cache.clear()
