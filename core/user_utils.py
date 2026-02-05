from allauth.socialaccount.models import SocialAccount


def get_user_email(user):
    email = (user.email or "").strip()
    if email:
        return email

    social = SocialAccount.objects.filter(user=user).first()
    if social and isinstance(social.extra_data, dict):
        email = (social.extra_data.get("email") or "").strip()
        if email:
            return email

    return ""
