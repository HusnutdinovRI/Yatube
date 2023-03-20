from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
        labels = {'first_name': 'Имя',
                  'last_name': 'Фамилия',
                  'username': 'Имя пользователя',
                  'email': "Электронная почта",
                  }
        help_texts = {'first_name': 'Введите Ваше имя',
                      'last_name': 'Введите вашу фамилию',
                      'username': 'Придумайте имя пользователя.'
                                  ' Обязательное поле. Не более 150 символов.'
                                  ' Только буквы, цифры и символы @/./+/-/_. ',
                      'email': "Введите вашу электронную почту",

                      }
