import xbmcgui

class DialogProgressWrapper(object):
    def __init__(self, title, progress_string):
        self._dialog = xbmcgui.DialogProgress()
        self._progress_string = progress_string
        self._dialog.create(title)

    def update(self, precentage, name=None):
        text = ""
        if name:
            text = self._progress_string % name
        return self._dialog.update(precentage, text)

    def iscanceled(self):
        return self._dialog.iscanceled()

    def close(self):
        return self._dialog.close()
