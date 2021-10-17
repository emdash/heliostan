# This is not a pure python script!
#
# This is a visualization is intended to be run in
# `https://githum.com/emdash/cairo_sandbox`.
#
# I used this script to explore the apparent sun positoins through different
# 24-hour periods hour periods at different points on the globe.
#
# Latitude, longitude, and the day of the year are inputs.

import datetime
import pysolar.solar as solar

SECONDS_PER_DAY = 60 * 60 * 24

def clamp(lower, x, upper): return min(upper, max(lower, x))

if __name__ == "init":
    params.define("resolution",     Numeric(4, 100, 1, 12))
    params.define("color_altitude", Color(1, 0, 0, 1))
    params.define("color_azimuth",  Color(1, 1, 0, 1))
    params.define("line_width",     Numeric(1.0, 50.0, 0.5, 1.0))
    params.define("latitude",       Numeric(-90, 90, 1, 45))
    params.define("longitude",      Numeric(-180, 180, 1, -123))
    params.define("year",           Infinite(2021)),
    params.define("month",          Numeric(1, 12, 1, 1))
    params.define("day",            Numeric(1, 31, 1, 1))
    params.define("scale_x",        Numeric(0, 1000, 0.1, 1.0))
    params.define("scale_y",        Numeric(0, 1000, 0.1, 1.0))
    params.define("font",           Font("monospace 2"))
    params.define("offset_x",       Infinite(0))
    params.define("offset_y",       Infinite(0))
else:
    # cache the frequently-used params to locals
    n     = int(params["resolution"])
    lat   = float(params["latitude"])
    lon   = float(params["longitude"])
    font  = params["font"]
    start = datetime.datetime(
        int(params["year"]),
        int(params["month"]),
        int(params["day"]),
        tzinfo = datetime.timezone.utc
    )

    # this value comes up a few times
    seconds = SECONDS_PER_DAY / n

    # set the line width in default units
    cr.set_line_width(float(params["line_width"]))
    
    with helpers.box(window.inset(10), clip=False) as layout:
        # XXX: dubious
        cr.translate(layout.west().x + float(params["offset_x"]), 0)

        # now that we have a concrete pixel width, calculate the spacing
        # between sample points.
        x_spacing = layout.width / n

        # calculate the mapping from x coord to time of day
        times = [
            (i * x_spacing, start + datetime.timedelta(0, i * seconds))
            for i in range(n)
        ]

        # draw the horizontal scale
        with helpers.save():
            cr.translate(0, layout.south().y - 5)
            for x, t in times:
                cr.move_to(x, layout.center.y)
                helpers.center_text("%02d:%02d" % (t.hour, t.minute), font)

        # draw the vertical scale
        with helpers.save():
            cr.translate(10, layout.north().y)
            for i in range(0, 180, 10):
                cr.move_to(0, i)
                helpers.center_text("%d deg" % (180 - i), font)

        # draw the azimuth trace
        with helpers.save():
            cr.translate(0, float(params["offset_y"]))
            cr.scale(1.0, float(params["scale_y"]))
            helpers.polygon(*[
                Point(x, clamp(-180, solar.get_azimuth(lat, lon, t), 180))
                for (x, t) in times
            ], close=False)
        cr.set_source(params["color_azimuth"])
        cr.stroke()

        # draw the zenith trace
        with helpers.save():
            cr.translate(0, float(params["offset_y"]))
            cr.scale(1.0, float(params["scale_y"]))

            helpers.polygon(*[
                Point(x, clamp(0, solar.get_altitude(lat, lon, t), 180))
                for (x, t) in times
            ], close=False)
        cr.set_source(params["color_altitude"])
        cr.stroke()
