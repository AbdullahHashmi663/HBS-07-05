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

def hotel_info(request):
    """
    Context processor to include hotel information on all pages.
    """
    try:
        from .models import HotelInfo
        info = HotelInfo.get_info()
        return {'hotel_info': info}
    except Exception:
        pass
    
    return {'hotel_info': None} 