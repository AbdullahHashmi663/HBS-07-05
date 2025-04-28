def theme_settings(request):
    """
    Context processor to include theme settings for the authenticated user.
    """
    if request.user.is_authenticated:
        try:
            from .models import ThemeSettings
            theme_settings, created = ThemeSettings.objects.get_or_create(user=request.user)
            return {'user_theme_settings': theme_settings}
        except Exception:
            pass
    
    return {'user_theme_settings': None} 