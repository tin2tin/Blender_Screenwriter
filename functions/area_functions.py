def findTextEditor(context):
    text_editors = []
    for window in context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == "TEXT_EDITOR": text_editors.append(area)
    return text_editors