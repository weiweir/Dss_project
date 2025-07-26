from django import forms

class BusinessMatchForm(forms.Form):
    address = forms.CharField(label="Địa chỉ trung tâm", max_length=200)
    radius = forms.IntegerField(label="Bán kính (m)", min_value=100, max_value=5000, initial=2000)

    price_min = forms.IntegerField(
        label="Giá tối thiểu", min_value=1, required=False,
        widget=forms.NumberInput(attrs={"placeholder": "VD: 1"})
    )
    price_max = forms.IntegerField(
        label="Giá tối đa", min_value=1, required=False,
        widget=forms.NumberInput(attrs={"placeholder": "VD: 4"})
    )

    customer_target = forms.ChoiceField(
        label="Khách hàng mục tiêu",
        choices=[
            ("general", "Khách hàng phổ thông"),
            ("student", "Học sinh / Sinh viên"),
            ("office", "Dân văn phòng"),
            ("family", "Gia đình"),
            ("tourist", "Khách du lịch"),
        ],
        initial="general"
    )
