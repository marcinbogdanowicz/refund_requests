from django import forms


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
