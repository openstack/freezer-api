# app/i18n.py

import oslo_i18n

_translators = oslo_i18n.TranslatorFactory(domain='freezer-api')

# The primary translation function using the well-known name "_"
_ = _translators.primary

# contextual_form and plural_from don't work under oslo.i18n 1.5.0
# The contextual translation function using the name "_C"
# _C = _translators.contextual_form

# The plural translation function using the name "_P"
# _P = _translators.plural_form

# Translators for log levels.
#
# The abbreviated names are meant to reflect the usual use of a short
# name like '_'. The "L" is for "log" and the other letter comes from
# the level.
_LI = _translators.log_info
_LW = _translators.log_warning
_LE = _translators.log_error
_LC = _translators.log_critical
