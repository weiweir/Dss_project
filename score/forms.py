from django import forms
import json, os

# Tải danh sách category từ file categories.json
CATEGORY_FILE = os.path.join(os.path.dirname(__file__), 'data', 'categories.json')
with open(CATEGORY_FILE, 'r', encoding='utf-8') as f:
    categories = json.load(f)

CATEGORY_CHOICES = [("", "Tất cả các loại hình")] + [(c["category_id"], c["category_name"]) for c in categories]

class CombinedScoreForm(forms.Form):
    address = forms.CharField(
        label="Nhập địa chỉ trung tâm",
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'VD: 123 Nguyễn Huệ, Quận 1, TP.HCM'})
    )

    radius = forms.IntegerField(
        label="Bán kính tìm kiếm (mét)",
        min_value=100,
        max_value=5000,
        initial=1000,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    category = forms.ChoiceField(
        label="Loại hình kinh doanh",
        choices=CATEGORY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    num_clusters = forms.IntegerField(
        label="Số cụm phân tích",
        min_value=2,
        max_value=10,
        initial=3,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'title': 'Chọn số cụm để phân tích (2-10)'
        })
    )

    min_price = forms.IntegerField(
        label="Khoảng giá tối thiểu",
        min_value=1,
        max_value=4,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    max_price = forms.IntegerField(
        label="Khoảng giá tối đa",
        min_value=1,
        max_value=4,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    # Các trọng số DSS
    w_distance = forms.FloatField(label="Trọng số Khoảng cách", min_value=0, max_value=5, initial=1.5)
    w_competitors = forms.FloatField(label="Trọng số Đối thủ", min_value=0, max_value=5, initial=1.2)
    w_rating = forms.FloatField(label="Trọng số Rating", min_value=0, max_value=5, initial=0.8)
    w_diversity = forms.FloatField(label="Trọng số Đa dạng", min_value=0, max_value=5, initial=0.5)
    w_schools = forms.FloatField(label="Trọng số Gần trường học", min_value=0, max_value=5, initial=1.0)
    w_residential = forms.FloatField(label="Trọng số Gần khu dân cư", min_value=0, max_value=5, initial=1.0)