from dataclasses import dataclass

@dataclass
class Profile:
    user_id: str
    display_name: str

def normalize_display_name(display_name: str) -> str:
    return display_name.strip()

def render_profile(profile: Profile) -> str:
    name = normalize_display_name(profile.display_name)
    return f"{name} ({profile.user_id})"
