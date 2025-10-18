from django import forms

class ProductForm(forms.Form):
    nombre = forms.CharField(max_length=200, label="Nombre")
    categoria = forms.CharField(max_length=100, label="Categoría")
    descripcion = forms.CharField(widget=forms.Textarea, required=False, label="Descripción")
    precio = forms.DecimalField(max_digits=10, decimal_places=2, label="Precio")
    cantidad = forms.IntegerField(min_value=0, label="Cantidad")
    fecha_vencimiento = forms.DateField(required=False, label="Fecha de vencimiento (YYYY-MM-DD)",
                                       widget=forms.TextInput(attrs={"placeholder": "YYYY-MM-DD"}))
