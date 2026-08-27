from variables import popups


class Popup:
    def __init__(self, content, pos_y, pos_x):
        self.content = content
        self.pos_y = pos_y
        self.pos_x = pos_x

        self.content_listed = [
            [key[i:i+2].ljust(2) for i in range(0, len(key), 2)]
            for key in content
        ]

        self.res_y = len(self.content_listed)
        self.res_x = max(map(len, self.content_listed), default=0)

def new_popup(content, pos_y, pos_x):
    popups[0] = Popup(content, pos_y, pos_x)
