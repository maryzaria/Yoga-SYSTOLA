from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class SystolaSocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form=form)
        if not user.email:
            extra = sociallogin.account.extra_data or {}
            email = (extra.get("email") or "").strip()
            if not email and isinstance(extra.get("emails"), list):
                for item in extra.get("emails", []):
                    value = (item or "").strip()
                    if value:
                        email = value
                        break
            if not email and isinstance(extra.get("emailAddresses"), list):
                for item in extra.get("emailAddresses", []):
                    if isinstance(item, dict):
                        value = (item.get("value") or "").strip()
                        if value:
                            email = value
                            break
            if email:
                user.email = email
                user.save(update_fields=["email"])
        return user
