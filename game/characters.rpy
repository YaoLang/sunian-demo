define s = Character("苏念", color="#c48b9f", who_outlines=[(1, "#00000055")], what_font="NotoSansCJKsc.otf")
define e = Character("叶辰", color="#6a8caf", what_font="NotoSansCJKsc.otf")
define narrator = Character(None, what_font="NotoSansCJKsc.otf")

transform center_sprite:
    xalign 0.5
    yalign 1.0
    zoom 0.55

image sunian normal = "images/sunian normal.png"
image sunian smile = "images/sunian smile.png"
image sunian surprised = "images/sunian surprised.png"
image sunian shy = "images/sunian shy.png"
image sunian worry = "images/sunian worry.png"

image bg campus = "images/bg campus.png"
image bg clubroom = "images/bg clubroom.png"
image bg hallway = "images/bg hallway.png"

init python:
    _cjk = "NotoSansCJKsc.otf"
    for _style_name in ("default", "say_dialogue", "say_label", "say_thought", 
                        "gui_text", "input", "input_prompt", "block", 
                        "history_text", "history_name", "main_menu_text", 
                        "main_menu_title", "navigation_button_text", 
                        "choice_button_text", "confirm_prompt", "about_text", 
                        "about_label", "prefs_label", "quick_button_text"):
        try:
            getattr(style, _style_name).font = _cjk
        except Exception:
            pass
