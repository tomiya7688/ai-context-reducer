# Profile display

A profile has a stable `user_id` and a user-editable `display_name`.

`normalize_display_name` removes only leading and trailing whitespace.
`render_profile` must use the normalized display name while preserving the original user ID.
