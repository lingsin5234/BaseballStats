from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit
from crispy_forms.bootstrap import InlineRadios

# constants
YEARS = ((2019, 2019), (2018, 2018), (2017, 2017), (2016, 2016), (2015, 2015),
         (2014, 2014), (2013, 2013), (2012, 2012), (2011, 2011), (2010, 2010))


class GetYear(forms.Form):
    get_year = forms.ChoiceField(choices=YEARS, widget=forms.RadioSelect)

    # doesn't seem to do anything below....
    def __init__(self, *args, **kwargs):
        super(GetYear, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            InlineRadios('get_year'),
            ButtonHolder('submit', 'Submit', css_class='button white')
        )
