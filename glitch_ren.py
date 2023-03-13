"""renpy
init python:
"""
class glitch(renpy.Displayable):
    """
    `randomkey`
        Follows the rules of the random modume's seed function.
        If not set, a random seed is generated when the transform is applied,
        and stays the same afterwards.
        If you want the effect to be random for each render operation, set to None.

    `chroma`
        Boolean, whether to apply the chromatic aberration effect.

    `minbandheight`
        Minimum height of each slice.

    `offset`
        The offset of each slice will be between -offset and offset pixels.

    `nslices`
        Number of slicings to do (the number of slices will be nslices + 1).
        Setting this to 0 is not supported.
        None (the default) makes it random.
    """

    NotSet = object()

    def __init__(self, child, *, randomkey=NotSet, chroma=True, minbandheight=1, offset=30, nslices=None, **properties):
        super().__init__(**properties)
        self.child = renpy.displayable(child)
        if randomkey is self.NotSet:
            randomkey = renpy.random.random()
        self.randomkey = randomkey
        self.chroma = chroma
        self.minbandheight = minbandheight
        self.offset = offset
        self.nslices = nslices

    def render(self, width, height, st, at):
        child = self.child
        child_render = renpy.render(child, width, height, st, at)
        cwidth, cheight = child_render.get_size()
        if not (cwidth and cheight):
            return child_render
        render = renpy.Render(cwidth, cheight)
        randomobj = renpy.random.Random(self.randomkey)
        chroma = self.chroma and renpy.display.render.models
        offset = self.offset
        minbandheight = self.minbandheight
        nslices = self.nslices
        if nslices is None:
            nslices = min(int(cheight/minbandheight), randomobj.randrange(10, 21))

        theights = sorted(randomobj.randrange(cheight+1) for k in range(nslices)) # y coordinates demarcating all the strips
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

class animated_glitch(glitch):
    """
    Glitches in a way that changes over time, but consistently, unlike glitch(randomkey=None).
    Sets a timeout at the beginning. At the end of each timeout, sets a new one and changes the glitching.

    `timeout_base`
        The time in seconds between two changes of the glitching.
        Can be either single float (or integer) value, or a tuple of two values between which the timeout
        will be chosen following a uniform distribution, respecting the randomkey.
        Defaults to .1 second.

    `timeout_vanilla`
        The length in seconds of the periods of time over which the child will be shown without any glitch.
        Same values and meaning as `timeout_base`, except that if False, the child will never be shown without glitching.
        If `timeout_base` is passed, defaults to the same value. Otherwise, defaults to (1, 3).
    """

    def __init__(self, *args, timeout_base=None, timeout_vanilla=None, **kwargs):
        super().__init__(*args, **kwargs)
        if timeout_vanilla is None:
            if timeout_base is None:
                timeout_vanilla = (1, 3)
            else:
                timeout_vanilla = timeout_base
        if timeout_base is None:
            timeout_base = .1

        self.timeout_base = timeout_base
        self.timeout_vanilla = timeout_vanilla
        self.set_timeout(vanilla=(timeout_vanilla is not False))

    def set_timeout(self, vanilla, st=0):
        if vanilla:
            timeout = self.timeout_vanilla
        else:
            timeout = self.timeout_base

        if not isinstance(timeout, (int, float)):
            timeout = renpy.random.Random(self.randomkey).uniform(*timeout)

        self.timeout = timeout + st
        self.showing_vanilla = vanilla

    def render(self, width, height, st, at):
        vanilla = self.showing_vanilla

        if st >= self.timeout:
            randomkey = self.randomkey
            randomobj = renpy.random.Random(randomkey)
            self.randomkey = randomobj.random()

            # determine whether to show vanilla or not
            if vanilla or (self.timeout_vanilla is False):
                # if we were showing it or if showing it is disabled
                vanilla = False
            else:
                vanilla = (randomobj.random() < .3)

            self.set_timeout(vanilla, st)

        renpy.redraw(self, st-self.timeout)

        if vanilla:
            return renpy.render(self.child, width, height, st, at)
        else:
            return super().render(width, height, st, at)

class squares_glitch(renpy.Displayable):
    """
    `squareside`
        The size, in pixels, of the side of the squares the child image will be cut to. This will
        be adjusted so that all the "squares" (rectangles, really) have the same width and the
        same height, and that none is cut at the borders of the image. Defaults to 20 pixels.

    `chroma`
        The probability for each square to get a chromatic effect. Defaults to .25.

    `permutes`
        The percentage of squares which will be moved to another square's place. If not passed,
        defaults to a random value between .1 and .4.
    """

    NotSet = object()

    def __init__(self, child, *args, randomkey=NotSet, **kwargs):
        super().__init__()
        self.child = renpy.displayable(child)
        self.args = args
        if randomkey is self.NotSet:
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
