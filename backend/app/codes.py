"""
Error and message codes for API responses.
Frontend uses these keys for i18n translation; backend returns only the code.

API contract: 4xx/5xx responses have JSON body { "code": "<key>" }.
Frontend should map each key to a translated string per locale.
"""

# Auth
AUTH_EMAIL_ALREADY_REGISTERED = "auth.email_already_registered"
AUTH_INVALID_CREDENTIALS = "auth.invalid_credentials"
AUTH_USER_INACTIVE = "auth.user_inactive"
AUTH_USER_LOCKED = "auth.user_locked"
AUTH_NOT_AUTHENTICATED = "auth.not_authenticated"
AUTH_INVALID_OR_EXPIRED_TOKEN = "auth.invalid_or_expired_token"
AUTH_LOGGED_OUT = "auth.logged_out"

# Network
NETWORK_NOT_FOUND = "network.not_found"
NETWORK_NOT_FOUND_OR_DENIED = "network.not_found_or_denied"
NETWORK_FORBIDDEN = "network.forbidden"
NETWORK_MEMBER_USER_NOT_FOUND = "network.member_user_not_found"
NETWORK_MEMBER_ALREADY_IN_NETWORK = "network.member_already_in_network"
NETWORK_MEMBER_FORBIDDEN = "network.member_forbidden"
NETWORK_MEMBER_CANNOT_CHANGE_OWNER = "network.member_cannot_change_owner"
NETWORK_MEMBER_CANNOT_REMOVE_OWNER = "network.member_cannot_remove_owner"
NETWORK_MEMBER_REMOVED = "network.member_removed"

# Family
FAMILY_NOT_FOUND_OR_DENIED = "family.not_found_or_denied"
FAMILY_FORBIDDEN = "family.forbidden"

# Member (family member)
MEMBER_NOT_FOUND_OR_DENIED = "member.not_found_or_denied"
MEMBER_FORBIDDEN = "member.forbidden"
MEMBER_LINK_USER_ALREADY_LINKED = "member.link_user_already_linked"
MEMBER_REMOVED = "member.removed"

# Marriage
MARRIAGE_NOT_FOUND_OR_DENIED = "marriage.not_found_or_denied"
MARRIAGE_SAME_MEMBER = "marriage.same_member"
MARRIAGE_DIFFERENT_NETWORK = "marriage.different_network"
MARRIAGE_ALREADY_ACTIVE = "marriage.already_active"
MARRIAGE_FORBIDDEN = "marriage.forbidden"
MARRIAGE_MEMBER_NOT_IN_FAMILY = "marriage.member_not_in_family"
