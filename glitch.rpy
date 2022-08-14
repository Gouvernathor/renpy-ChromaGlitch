transform chromatic_offset(child, chzoom=1.01):
    Fixed(
          Transform(child, alpha=.0),
          Transform(child, xalign=.0, xzoom=chzoom, gl_color_mask=(False, False, True, True)),
          Transform(child, xalign=.5, xzoom=chzoom, gl_color_mask=(False, True, False, True)),
          Transform(child, xalign=1.0, xzoom=chzoom, gl_color_mask=(True, False, False, True)),
          fit_first=True)
    crop (.0, .0, 1.0, 1.0)
    crop_relative True

init python:
    class glitch(renpy.Displayable):
        def __init__(self, child, *args, **kwargs):
            super().__init__()
            self.child = renpy.displayable(child)
            self.args = args
            self.kwargs = kwargs

        def render(self, width, height, st, at):
            cwidth, cheight = renpy.render(self.child, width, height, st, at).get_size()
            return renpy.render(self.glitch(self.child,
                                            cwidth, cheight,
                                            *self.args, **self.kwargs),
                                width, height,
                                st, at)

        @staticmethod
        def glitch(child, cwidth, cheight, randomobj=renpy.random.Random(), chroma=None, minbandheight=1, offset=30, crop=False):
            if chroma is None and renpy.display.render.models:
                chroma = True
            # child's width and height
            if not (cwidth and cheight):
                return child
            lizt = [] # liste of strips
            offt = 0 # next strip's lateral offset
            theights = [randomobj.randint(0, cheight) for k in range(min(cheight, randomobj.randint(20, 40)//2))]
            theights.sort() # coordinates demarcating all the strips
            fheight = 0 # sum of the size of all the strips added this far
            while fheight<cheight:
                # theight is the height of this particular strip
                if theights:
                    theight = max(theights.pop(0)-fheight, minbandheight)
                else:
                    cheight-theight
                band = Transform(child,
                                 # crop=(-offt, fheight, cwidth, theight),
                                 crop=(0, fheight, cwidth, theight),
                                 xoffset=offt,
                                 )
                if chroma:
                    band = chromatic_offset(Flatten(band), chzoom=1.0+.5*offt/cwidth)
                lizt.append(band)
                fheight += theight
                if offt:
                    offt = 0
                else:
                    offt = randomobj.randint(-offset, offset)
            crop = crop or None
            return Fixed(Transform(child, alpha=.0),
                         VBox(*lizt),
                         fit_first=True,
                         crop_relative=crop or False,
                         crop=crop and (0, 0, 1.0, 1.0),
                         )

        def __eq__(self, other):
            return (type(self) == type(other)) and (self.args == other.args) and (self.kwargs == other.kwargs)
