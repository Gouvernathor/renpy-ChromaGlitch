# renpy-ChromaGlitch
A way to display images (or other displayables) with a DDLC-like glitch effect offsetting slices of the image laterally and optionally adding chromatic aberration effects on the glitched slices.

![](sample_nochroma.png)
![](sample_chroma.png)

The `glitch.rpy` file contains the code itself.

## Howto glitch
`glitch` is a transform (because it takes a displayable and returns a displayable).
Its 6 parameters are :
- `child` : the displayable (~= image) on which the effect is applied. This is the only required argument.
- `randomkey` : the key given to the random object used to generate the slices heights and offsets. This must match [the random module's specfications](https://docs.python.org/3/library/random.html#random.seed). A given image glitched with a given non-None key will always, always, look the same. A glitched image with no key, or with a None key, will look differently every time Ren'Py renders it. Use this to make the glitching reliable (in an animation for example). Defaults to None, and this is a keyword-only argument because reasons.
- `chroma` : boolean indicating whether or not to apply chromatic aberration effects to the glitched tranches. Defaults to True.
- `minbandheight` : minimum height of a slice, in pixels. Defaults to 1.
- `offset` : a positive integer. The actual offset given to a glitched slice will be comprised between -offset and +offset. Defaults to 30.
- `crop` : boolean indicating whether or not to crop the resulting image to make it fit the size of the original image. Defaults to False.

Then, you can directly show it using `show expression glitch("eileen happy") as beautifulcharacter` (I strongly recommand using the `as` clause).
You can also apply it as a transform, with `show eileen at glitch` or `show eileen at functools.partial(glitch, chroma=False)` or even `show layer master at glitch`.

It is also possible to define it directly as an image, simply using `image eileen glitched = glitch("eileen", offset=20)`
(it was not possible in previous versions of ChromaGlitch, but now it's fixed).

## Chromatic aberration

The chromatic_offset transform can be used on a standalone basis, especially to apply it to the master layer with `show layer master at chromatic_offset` or `at chromatic_offset(chzoom=1.05)`.
The aberration effect is applied laterally, on a technical note the red, green and blue layers of the image are stretched horizontally and then offset laterally with different values.
It takes one optional parameter, chzoom, which determines exactly how much the layers are stretched. At 1.0 the layers are not streched and the effect is invisible, at lower than 1.0 the left and right boundaries are visible on the sides of the image, so advised values are greater than but close to 1.0. Default is 1.01.

## Terms of use
Use it freely in any project. If you liked it, you can drop my name in the credits with a link to this repo 🥰
