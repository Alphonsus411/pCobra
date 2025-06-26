import gettext
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
LOCALE_DIR = os.path.join(ROOT_DIR, 'frontend', 'docs', 'locale')

_ = gettext.gettext


def setup_gettext(lang: str | None = None):
    """Inicializa gettext y devuelve la función de traducción."""
    selected = lang or os.environ.get('COBRA_LANG', 'es')
    translation = gettext.translation(
        'cobra', localedir=LOCALE_DIR, languages=[selected], fallback=True
    )
    global _
    _ = translation.gettext
    return _
