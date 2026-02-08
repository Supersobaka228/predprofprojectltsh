from typing import Tuple

from django.contrib.auth import get_user_model

User = get_user_model()

ROLE_LABELS = {
    'student': 'Ученик',
    'cook': 'Повар',
    'admin_main': 'Администратор',
}


def get_profile_display_name(user: User) -> str:
    first = (getattr(user, 'first_name', '') or '').strip()
    last = (getattr(user, 'last_name', '') or '').strip()
    if first or last:
        return ' '.join(part for part in (first, last) if part)
    email = getattr(user, 'email', '') or ''
    return email or str(getattr(user, 'id', ''))


def get_profile_role_label(user: User) -> str:
    role = getattr(user, 'role', '')
    return ROLE_LABELS.get(role, 'Пользователь')

