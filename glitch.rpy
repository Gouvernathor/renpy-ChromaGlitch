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
        def __init__(self, child, *args, randomkey=None, **kwargs):
            super().__init__()
            self.child = renpy.displayable(child)
            self.args = args
            self.randomkey = randomkey
            self.kwargs = kwargs

        def render(self, width, height, st, at):
            cwidth, cheight = renpy.render(self.child, width, height, st, at).get_size()
            return renpy.render(self.glitch(self.child,
                                            cwidth, cheight, renpy.random.Random(self.randomkey),
                                            *self.args, **self.kwargs),
                                width, height,
                                st, at)

        @staticmethod
        def glitch(child, cwidth, cheight, randomobj, chroma=True, minbandheight=1, offset=30, crop=False):
            chroma &= renpy.display.render.models
            if not (cwidth and cheight):
                return child
            lizt = [] # liste of strips
            offt = 0 # next strip's lateral offset
            theights = sorted(randomobj.randint(0, cheight) for k in range(min(cheight, randomobj.randint(10, 20)))) # y coordinates demarcating all the strips
            fheight = 0 # sum of the size of all the strips added this far
            while fheight<cheight:
                # theight is the height of this particular strip
                if theights:
                    theight = max(theights.pop(0)-fheight, minbandheight)
                else:
                    theight = cheight-theight
                band = Transform(child, crop=(0, fheight, cwidth, theight))
                if chroma:
                    band = chromatic_offset(band, chzoom=1.0+.5*offt/cwidth)
                band = Transform(band, pos=(offt, absolute(fheight)), subpixel=True)
                lizt.append(band)
                fheight += theight
                if offt:
                    offt = 0
                else:
                    offt = randomobj.randint(-offset, offset)
            crop = crop or None
            return Fixed(Transform(child, alpha=.0),
                         *lizt,
                         fit_first=True,
                         crop_relative=crop or False,
                         crop=crop and (0, 0, 1.0, 1.0),
                         )

        def __eq__(self, other):
            return (type(self) == type(other)) and (self.args == other.args) and (self.kwargs == other.kwargs)

    class squares_glitch(glitch):
        @staticmethod
        def glitch(child, cwidth, cheight, randomobj, squareside=20, chroma=.25, permutes=None):
            if not renpy.display.render.models:
                chroma = False
            if not (cwidth and cheight):
                return child

            ncols = round(cwidth/squareside)
            nrows = round(cheight/squareside)
            square_width = absolute(cwidth/ncols)
            square_height = absolute(cheight/nrows)

            lizt = []
            for y in range(nrows):
                for x in range(ncols):
                    lizt.append(Transform(child,
                                          crop=(absolute(x*square_width), absolute(y*square_height), square_width, square_height),
                                          subpixel=True,
                                          ))

            if permutes is None:
                permutes = randomobj.randrange(10, 40)/100 # between 10% and 40%
            permutes = round(permutes*ncols*nrows)
            permute_a = randomobj.sample(range(ncols*nrows), permutes)
            permute_b = randomobj.sample(range(ncols*nrows), permutes)

            for a, b in zip(permute_a, permute_b):
                lizt[a], lizt[b] = lizt[b], lizt[a]

            for k, el in enumerate(lizt):
                if randomobj.random() < chroma:
                    lizt[k] = Transform(el,
                                        gl_color_mask=(randomobj.random()<.33, randomobj.random()<.33, randomobj.random()<.33, True),
                                        # matrixcolor=HueMatrix(randomobj.random()*360),
                                        )

            return Grid(ncols, nrows, *lizt)
