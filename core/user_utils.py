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

        if isinstance(social.extra_data.get("emails"), list):
            for item in social.extra_data["emails"]:
                value = (item or "").strip()
                if value:
                    return value

        if isinstance(social.extra_data.get("emailAddresses"), list):
            for item in social.extra_data["emailAddresses"]:
                if isinstance(item, dict):
                    value = (item.get("value") or "").strip()
                    if value:
                        return value

    return ""
