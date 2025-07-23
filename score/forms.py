from django import forms

class ScoreForm(forms.Form):
    address = forms.CharField(label="Địa chỉ", max_length=255)
    w_distance = forms.FloatField(label="Trọng số khoảng cách", min_value=0, max_value=5, initial=1)
    w_competitors = forms.FloatField(label="Trọng số đối thủ", min_value=0, max_value=5, initial=1)
    w_rating = forms.FloatField(label="Trọng số rating", min_value=0, max_value=5, initial=1)
    w_diversity = forms.FloatField(label="Trọng số đa dạng", min_value=0, max_value=5, initial=1)
