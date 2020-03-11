from django import forms

# constants
YEARS = ((2019, 2019), (2018, 2018), (2017, 2017), (2016, 2016), (2015, 2015),
         (2014, 2014), (2013, 2013), (2012, 2012), (2011, 2011), (2010, 2010))


class GetYear(forms.Form):
    get_year = forms.ChoiceField(choices=YEARS, widget=forms.RadioSelect)
