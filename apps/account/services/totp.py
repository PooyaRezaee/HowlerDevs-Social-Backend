import pyotp


def generate_totp_secret():
    return pyotp.random_base32()


def setup_totp_for_user(user):
    secret = generate_totp_secret()
    user.totp_secret = secret
    user.is_2fa_enabled = False
    user.save(update_fields=["totp_secret", "is_2fa_enabled"])
    return secret


def verify_totp_code(user, code):
    if not user.totp_secret:
        return False
    totp = pyotp.TOTP(user.totp_secret)
    return totp.verify(code, valid_window=1)
