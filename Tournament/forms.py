# Формы
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, MinLengthValidator, MaxLengthValidator
from django.core.exceptions import ValidationError
from .models import Profile, TournamentObject

username_validators = [
    RegexValidator(
        r'^[a-zA-Z0-9_]+$',  # Обновленное регулярное выражение для латинских букв, цифр и подчеркиваний
        message="Имя пользователя может содержать только латинские буквы, цифры и подчеркивания."
    ),
    MinLengthValidator(4, message="Имя пользователя должно быть не менее 4 символов."),
    MaxLengthValidator(20, message="Имя пользователя не должно превышать 20 символов.")
]

class CustomLoginForm(AuthenticationForm):
    remember_me = forms.BooleanField(required=False, label='Запомнить меня')

    def __init__(self, *args, **kwargs):
        super(CustomLoginForm, self).__init__(*args, **kwargs)
        self.label_suffix = ""  # Убирает двоеточие после метки
        self.fields['username'].label = "Логин"  # Изменяет метку поля "username"
        self.fields['remember_me'].widget.attrs.update({'class': 'form-check-input'})

    def confirm_login_allowed(self, user):
        if user.profile.is_verified == False and user.groups.filter(name='Организатор').exists():
            raise ValidationError(
                "Ваш аккаунт еще не верифицирован. Пожалуйста, свяжитесь с администрацией для прохождения верификации.",
                code='unverified',
            )

    def get_user(self):
        user = super(CustomLoginForm, self).get_user()
        user.remember_me = self.cleaned_data.get('remember_me')
        return user
    
class CustomUserCreationForm(UserCreationForm):
    ACCOUNT_TYPE_CHOICES = [
        ('organizer', 'Организатор'),
        ('captain', 'Представитель команды'),
    ]
    
    account_type = forms.ChoiceField(
        choices=ACCOUNT_TYPE_CHOICES,
        required=True,
        label='Тип учетной записи',
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text='Выберите тип учетной записи.'
    )
    organization_name = forms.CharField(
        required=False,
        label='Название организации',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text='Обязательное поле для организаторов.'
    )
    phone_number = forms.CharField(
        required=True,
        label='Номер телефона',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text='Обязательное поле для организаторов.'
    )
    first_name = forms.CharField(
        required=False,
        label='Имя',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text='Обязательное поле для представителей команд.'
    )
    last_name = forms.CharField(
        required=False,
        label='Фамилия',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text='Обязательное поле для представителей команд'
    )
    email = forms.EmailField(
        required=True, 
        label='Email', 
        widget=forms.EmailInput(attrs={'class': 'form-control'}), 
        help_text='Обязательное поле. Укажите действующий адрес электронной почты.'
    )
    username = forms.CharField(
        label='Логин',
        validators=username_validators,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text='4-20 символов. Только латинские буквы, цифры и подчеркивания.'
    )

    class Meta:
        model = User
        fields = ("account_type", "organization_name", "phone_number", "first_name", "last_name", "email", "username", "password1", "password2")

    field_order = ["account_type", "organization_name", "phone_number", "first_name", "last_name", "email", "username", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        self.label_suffix = ""
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Пользователь с таким адресом электронной почты уже существует.")
        return email

    def clean_organization_name(self):
        organization_name = self.cleaned_data.get('organization_name')
        if organization_name and Profile.objects.filter(organization_name=organization_name).exists():
            raise ValidationError("Организация с таким названием уже существует.")
        return organization_name

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if Profile.objects.filter(phone_number=phone_number).exists():
            raise ValidationError("Пользователь с таким номером телефона уже существует.")
        return phone_number

    def save(self, commit=True):
        user = super(CustomUserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
            if self.cleaned_data["account_type"] == "organizer":
                Profile.objects.create(
                    user=user,
                    organization_name=self.cleaned_data["organization_name"],
                    phone_number=self.cleaned_data["phone_number"]
                )
            else:
                Profile.objects.create(user=user)
        return user

class RulesUploadForm(forms.ModelForm):
    class Meta:
        model = TournamentObject
        fields = ['rules_document']
        widgets = {
            'rules_document': forms.ClearableFileInput(attrs={'accept': '.pdf,.doc,.docx'}),
        }