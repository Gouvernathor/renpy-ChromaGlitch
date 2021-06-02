# renpy-ChromaGlitch
A way to display images (or other displayables) with a DDLC-like glitch effect offsetting slices of the image laterally and optionally adding chromatic aberration effects on the glitched slices.

![](sample_nochroma.png)
![](sample_chroma.png)

The `glitch.rpy` file contains the code itself.

## Howto
`glitch` is a function that can be used as a transform (because it takes a displayable as lone argument and returns a displayable).
Its 6 parameters are :
- `child` : the displayable (~= image) on which the effect is applied. This is the only required argument.
- `randomobj` : the random object used to generate the slices heights and offsets.
- `chroma` : boolean indicating whether or not to apply chromatic aberration effects to the glitched tranches. Defaults to True if the system can manage it (which needs gl2 or another model-based renderer to work).
- `minbandheight` : minimum height of a slice, in pixels. Defaults to 1.
- `offset` : a positive integer. The actual offset given to a glitched slice will be comprised between -offset and offset. Defaults to 30.
- `crop` : boolean indicating whether or not to crop the resulting image to make it fit the size of the original image. Defaults to False.

Then, you can define your glitched image as an image to show afterward, using `image glitched = glitch("beautifulcharacter angry")`, or you can also directly show it using `show expression glitch("beautifulcharacter angry") as beautifulcharacter` (I strongly recommand using the `as` clause).
You can also apply it as a transform, with `show eileen at glitch` or `show eileen at renpy.curry(glitch)(chroma=False)` or even `show layer master at glitch`.

## Terms of use
Use it freely in any project, just drop my name in the credits with a link to this repo if you liked it 🥰
