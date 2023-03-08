"""renpy
init python:
"""
class glitch(renpy.Displayable):
    _stableseed = object()

    def __init__(self, child, *, randomkey=_stableseed, chroma=True, minbandheight=1, offset=30, **properties):
        super().__init__(**properties)
        self.child = renpy.displayable(child)
        if randomkey is self._stableseed:
            randomkey = renpy.random.random()
        self.randomkey = randomkey
        self.chroma = chroma
        self.minbandheight = minbandheight
        self.offset = offset

    def render(self, width, height, st, at):
        child = self.child
        child_render = renpy.render(child, width, height, st, at)
        cwidth, cheight = child_render.get_size()
        if not (cwidth and cheight):
            return child
        render = renpy.Render(cwidth, cheight)
        randomobj = renpy.random.Random(self.randomkey)
        chroma = self.chroma and renpy.display.render.models
        offset = self.offset
        minbandheight = self.minbandheight

        theights = sorted(randomobj.randrange(cheight+1) for k in range(min(cheight, randomobj.randrange(10, 21)))) # y coordinates demarcating all the strips
        offt = 0 # next strip's lateral offset
        fheight = 0 # sum of the size of all the strips added this far
        while fheight<cheight:
            # theight is the height of this particular strip
            if theights:
                theight = max(theights.pop(0)-fheight, minbandheight)
            else:
                theight = cheight-theight

            slice_render = child_render.subsurface((0, fheight, cwidth, theight))

            if offt and chroma:
                for color_mask, chponder in (((False, False, True, True), 1.25), ((False, True, False, True), 1.), ((True, False, False, True), .75)):
                    chroma_render = slice_render.subsurface((0, 0, cwidth, theight))
                    chroma_render.add_property("gl_color_mask", color_mask)
                    render.blit(chroma_render, (round(offt*chponder), round(fheight)))

            else:
                render.blit(slice_render, (offt, round(fheight)))

            fheight += theight
            if offt:
                offt = 0
            else:
                offt = randomobj.randrange(-offset, offset+1)

        return render

    def visit(self):
        return [self.child]

class squares_glitch(renpy.Displayable):
    _stableseed = object()

    def __init__(self, child, *args, randomkey=_stableseed, **kwargs):
        super().__init__()
        self.child = renpy.displayable(child)
        self.args = args
        if randomkey is self._stableseed:
            randomkey = renpy.random.random()
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

    def __eq__(self, other):
        return (type(self) == type(other)) and (self.args == other.args) and (self.kwargs == other.kwargs)
