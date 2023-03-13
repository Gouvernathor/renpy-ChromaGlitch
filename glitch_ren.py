"""renpy
init python:
"""
import functools

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

    def __init__(self, child, *, randomkey=NotSet, chroma=.25, squareside=20, permutes=None, **properties):
        super().__init__(**properties)
        self.child = renpy.displayable(child)
        if randomkey is self.NotSet:
            randomkey = renpy.random.random()
        self.randomkey = randomkey
        self.chroma = chroma
        self.squareside = squareside
        if permutes is None:
            permutes = (.1, .4)
        self.permutes = permutes

    def render(self, width, height, st, at):
        child = self.child
        child_render = renpy.render(child, width, height, st, at)
        cwidth, cheight = child_render.get_size()
        if not (cwidth and cheight):
            return child_render
        render = renpy.Render(cwidth, cheight)
        randomobj = renpy.random.Random(self.randomkey)
        chroma = renpy.display.render.models and self.chroma
        squareside = self.squareside
        permutes = self.permutes

        mround = functools.cache(round)

        ncols = mround(cwidth/squareside)
        nrows = mround(cheight/squareside)
        square_width = cwidth/ncols
        square_height = cheight/nrows

        lizt = [] # list of subsurface renders
        for x in range(ncols):
            lisst = []
            lizt.append(lisst)
            xround = mround(x*square_width)
            wround = mround((x+1)*square_width) - xround
            for y in range(nrows):
                yround = mround(y*square_height)
                hround = mround((y+1)*square_height) - yround
                lisst.append(child_render.subsurface((xround, yround, wround, hround)))

        if not isinstance(permutes, (int, float)):
            permutes = randomobj.uniform(*permutes)
        permutes = mround(permutes*ncols*nrows)
        indices = [(x, y) for x in range(ncols) for y in range(nrows)]
        permute_a = randomobj.sample(indices, permutes)
        permute_b = randomobj.sample(indices, permutes)

        for (ax, ay), (bx, by) in zip(permute_a, permute_b):
            lizt[ax][ay], lizt[bx][by] = lizt[bx][by], lizt[ax][ay]

        for x, y in indices:
            ss = lizt[x][y]
            if randomobj.random() < chroma:
                mask = [randomobj.random()<.33, randomobj.random()<.5, True]
                randomobj.shuffle(mask)
                mask.append(True)
                ss.add_property("gl_color_mask", mask)
            render.blit(ss, (mround(x*square_width), mround(y*square_height)))

        return render

    def visit(self):
        return [self.child]
