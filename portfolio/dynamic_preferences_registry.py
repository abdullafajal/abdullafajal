from dynamic_preferences.types import IntegerPreference
from dynamic_preferences.preferences import Section
from dynamic_preferences.registries import global_preferences_registry

# we create some section objects to link related preferences together

general = Section('general')

# We start with a global preference
@global_preferences_registry.register
class TotalProject(IntegerPreference):
    section = general
    name = 'total_projects'
    default = 5
    required = True
    help_text = 'Total number of projects to display on the homepage.'


@global_preferences_registry.register
class TotalClient(IntegerPreference):
    section = general
    name = 'total_clients'
    default = 5
    required = True
    help_text = 'Total number of client to display on the homepage.'