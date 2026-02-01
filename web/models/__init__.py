from web.models.user import User, Role, Subscription, Plan, Payment
from web.models.file import UserFile, Report, Template, ContactMessage

# Modelleri doğrudan erişilebilir yap
__all__ = [
    'User', 'Role', 'Subscription', 'Plan', 'Payment',
    'UserFile', 'Report', 'Template', 'ContactMessage'
]
