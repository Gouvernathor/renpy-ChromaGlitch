# renpy-ChromaGlitch
A way to display images (or other displayables) with a DDLC-like glitch effect offsetting slices of the image laterally and optionally adding chromatic aberration effects on the glitched slices.

These effects were featured in [this YouTube video](https://www.youtube.com/watch?v=H2eg010UozE) by Visual Novel Design. Thanks to him !

![](sample_nochroma.png)
![](sample_chroma.png)

The `glitch.rpy` file contains the code itself.

## Howto glitch
`glitch` is a transform (because it takes a displayable and returns a displayable).
Its 6 parameters are :
- `child` : the displayable (~= image) on which the effect is applied. This is the only required argument.
- `randomkey` : the key given to the random object used to generate the slices heights and offsets. This must match [the random module's specifications](https://docs.python.org/3/library/random.html#random.seed). A given image glitched with a given non-None key will always, always, look the same. A glitched image with no key, or with a None key, will look differently every time Ren'Py renders it. Use this to make the glitching reliable (in an animation for example). Defaults to None, and this is a keyword-only argument because reasons.
- `chroma` : boolean indicating whether or not to apply chromatic aberration effects to the glitched tranches. Defaults to True.
- `minbandheight` : minimum height of a slice, in pixels. Defaults to 1.
- `offset` : a positive integer. The actual offset given to a glitched slice will be comprised between -offset and +offset. Defaults to 30.
- `crop` : boolean indicating whether or not to crop the resulting image to make it fit the size of the original image. Defaults to False.

Then, you can directly show it using `show expression glitch("eileen happy") as beautifulcharacter` (I strongly recommand using the `as` clause).
You can also apply it as a transform, with `show eileen at glitch` or `show eileen at functools.partial(glitch, chroma=False)` or even `show layer master at glitch`.

It is also possible to define it directly as an image, simply using `image eileen glitched = glitch("eileen", offset=20)`
(it was not possible in previous versions of ChromaGlitch, but now it's fixed).

Example :
```rpy
image eileen glitched:
    glitch("eileen happy", randomkey=83468468) # reliable slicing
    pause 1.0
    glitch("eileen happy", offset=60) # bigger and always-random slicing
    pause 0.1
    repeat
```

## Chromatic aberration

The chromatic_offset transform can be used on a standalone basis, especially to apply it to the master layer with `show layer master at chromatic_offset` or `at chromatic_offset(chzoom=1.05)`.
The aberration effect is applied laterally, on a technical note the red, green and blue layers of the image are stretched horizontally and then offset laterally with different values.
It takes one optional parameter, chzoom, which determines exactly how much the layers are stretched. At 1.0 the layers are not streched and the effect is invisible, at lower than 1.0 the left and right boundaries are visible on the sides of the image, so advised values are greater than but close to 1.0. Default is 1.01.

## Squares glitch

![](sample_squares.png)

This is a second type of glitch, which cuts the image into squares and does things to them.
It takes `child` and `randomkey`, which are the same as for the preceding glitch, and three aditional parameters.
- `squareside` : the size, in pixels, of the side of the squares the image will be cut to. This will be adjusted so that all the squares have the same size. Defaults to 20.
- `chroma` : the probability (0. - 1.) for each square to get a chromatic glitch. Defaults to .25.
- `permutes` : the percentage (0. - 1.) of squares which will change places with other squares. Defaults to a random percentage between 10% and 40%.

## Terms of use
Use it freely in any project. If you liked it, you can drop my name in the credits with a link to this repo 🥰
