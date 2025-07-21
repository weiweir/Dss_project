from django import forms
import json, os

CATEGORY_FILE = os.path.join(os.path.dirname(__file__), 'data', 'categories.json')
with open(CATEGORY_FILE, 'r', encoding='utf-8') as f:
    categories = json.load(f)

CATEGORY_CHOICES = [(c["category_id"], c["category_name"]) for c in categories]

class SearchForm(forms.Form):
    address = forms.CharField(label="Địa điểm", max_length=255, initial="Bưu điện trung tâm Sài Gòn")
    category = forms.ChoiceField(choices=CATEGORY_CHOICES, label="Loại hình kinh doanh")
    min_price = forms.ChoiceField(
        choices=[('', 'Không giới hạn'), (1, '1'), (2, '2'), (3, '3'), (4, '4')],
        required=False, label="Giá tối thiểu"
    )
    max_price = forms.ChoiceField(
        choices=[('', 'Không giới hạn'), (1, '1'), (2, '2'), (3, '3'), (4, '4')],
        required=False, label="Giá tối đa"
    )
    radius = forms.IntegerField(label="Bán kính (m)", initial=1000, min_value=100, max_value=5000)

    cluster_k = forms.IntegerField(
    label="Số lượng cụm muốn phân",
    min_value=1,
    max_value=10,
    initial=3,
    required=False,
    widget=forms.NumberInput(attrs={
        'type': 'range',
        'min': '1',
        'max': '10',
        'step': '1',
        'id': 'cluster_k_range',
        'oninput': 'updateClusterLabel(this.value)'
    }),
    help_text="Kéo để chọn số lượng cụm (1–10)"
)