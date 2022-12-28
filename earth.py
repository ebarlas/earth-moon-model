from skyfield import api
from skyfield import almanac

EVENT_VERNAL_EQUINOX = 0
EVENT_SUMMER_SOLSTICE = 1
EVENT_AUTUMNAL_EQUINOX = 2
EVENT_WINTER_SOLSTICE = 3

timescale = api.load.timescale()
ephemeris = api.load('de421.bsp')  # load the JPL ephemeris DE421 (covers 1900-2050)
greenwich = api.Topos('51.48 N', '0 W')


class Event:
    """
    Class composed of an event value and an event label string.
    """

    def __init__(self, value, label):
        self.value = value
        self.label = label

    def __repr__(self):
        return self.label


class EventTime:
    """
    Class composed of an Event object and a Skyfield Time object.
    """

    def __init__(self, event, time):
        self.event = event
        self.time = time

    def __repr__(self):
        return '{} at {}'.format(self.event, self.time.utc_strftime('%Y-%m-%d %H:%M:%S'))


class Earth:
    """
    Class composed of (1) earth orbit degrees (0 to 360), (2) earth rotation degrees (0 to 360),
    and (3) moon orbit degrees (0 to 360).

    These values are intended to serve as input to a physical model with the following configuration.

    The earth orbit reference point is Northern Hemisphere winter solstice, when the North Pole has
    its maximum tilt away from the sun. The earth rotation reference point is Greenwich. And the moon
    orbit reference point is new moon. Taken together, the physical model base position is solar noon
    in Greenwich at Northern Hemisphere winter solstice with a new moon.

    As a result, the physical model ought to apply these values as follows.
    Rotate bottom earth-orbit motor with by a number of degrees.
    Rotate middle earth-rotation motor by a number of degrees (minus earth-orbit degrees).
    Rotate upper moon-orbit motor by a number of degrees (minus earth-orbit degrees).

    Consider the following examples.
    Given earth-orbit degrees of 0 and earth-rotation degrees of 0, earth remains at solar noon in Greenwich on winter solstice.
    Given earth-orbit degrees of 90 and earth-rotation degrees of 270, earth is at solar noon in Greenwich on spring equinox.
    Given earth-orbit degrees of 180 and earth-rotation degree of 0, earth is at nadir in Greenwich on summer solstice.
    Given earth-orbit degrees of 180 and earth-rotation degree of 90, earth is at sunrise in Greenwich on summer solstice.
    """

    def __init__(self, eo_degrees, er_degrees, mo_degrees):
        assert 0 <= eo_degrees <= 360
        assert 0 <= er_degrees <= 360
        assert 0 <= mo_degrees <= 360
        self.eo_degrees = eo_degrees
        self.er_degrees = er_degrees
        self.mo_degrees = mo_degrees


def season_event_times(start, end):
    """
    Computes season event times between start and end.
    Returns list of EventTime objects.
    """
    t, y = almanac.find_discrete(start, end, almanac.seasons(ephemeris))
    return [EventTime(Event(event, almanac.SEASON_EVENTS[event]), time) for time, event in zip(t, y)]


def rise_set_event_times(start, end):
    """
    Computes sunrise and sunset times between start and end.
    Returns list of EventTime objects.
    """
    t, y = almanac.find_discrete(start, end, almanac.sunrise_sunset(ephemeris, greenwich))
    return [EventTime(Event(rise, 'Sunrise' if rise else 'Sunset'), time) for time, rise in zip(t, y)]


def noon_nadir_event_times(start, end):
    """
    Computes solar noon and nadir event times as midpoints between sunrise and sunset events.
    Returns list of EventTime objects.
    """
    result = []
    rs_event_times = rise_set_event_times(start, end)
    for x, y in zip(rs_event_times, rs_event_times[1:]):
        delta = y.time - x.time
        midpoint = timescale.tt_jd(x.time.tt + delta / 2)
        result.append(EventTime(Event(x.event.value, 'Solar noon' if x.event.value else 'Nadir'), midpoint))
    return result


def find_surrounding_events(events, time):
    """
    Locates the event times that straddle the input time.
    Returns tuple of EventTime objects.
    """
    for x, y in zip(events, events[1:]):
        if x.time.tt < time.tt < y.time.tt:
            return x, y


def surrounding_events(time, julian_time, events_func):
    """
    Locates the event times that straddle the input time.
    Returns tuple of objects provided by the input function.
    """
    t0 = timescale.tt_jd(time.tt - julian_time)
    t1 = timescale.tt_jd(time.tt + julian_time)
    sets = events_func(t0, t1)
    return find_surrounding_events(sets, time)


def relative_to_absolute_orbit_degrees(season, degrees):
    """
    Convert relative seasonal degrees (0 to 90) to absolute degrees on specialized scale.
    Scale goes from 0 to 360 from winter solstice (0), to vernal equinox (90),
    to summer solstice (180), to autumnal equinox (270), and back to winter solstice.
    """
    if season == EVENT_WINTER_SOLSTICE:  # 0 to 90
        return degrees
    if season == EVENT_VERNAL_EQUINOX:  # 90 to 180
        return 90 + degrees
    if season == EVENT_SUMMER_SOLSTICE:  # 180 to 270
        return 180 + degrees
    return 270 + degrees # 270 to 360


def position_as_percent(events, time):
    # total time separating a pair of events
    range = events[1].time - events[0].time

    # position within range [0, range]
    position = time - events[0].time

    # convert position to fractional value [0.0, 1.0]
    return position / range


def orbit_degrees_from_winter_solstice(time):
    """
    Computes earth orbit degrees of the input time relative to winter solstice on specialized scale.
    """
    # determine a pair of straddling season events
    evts = surrounding_events(time, 100, season_event_times)

    # convert fractional value to seasonal degrees offset [0, 90]
    degrees = position_as_percent(evts, time) * 90

    # adjust (+0, +90, +180, or +270) for season
    return relative_to_absolute_orbit_degrees(evts[0].event.value, degrees)


def rotation_degrees_from_solar_noon(time):
    """
    Computes earth rotation degrees of the input time relative to last solar noon.
    Scale goes from 0-360 between solar noon on the previous day and the next day.
    """
    # determine pair of solar noon/nadir events
    evts = surrounding_events(time, 1, noon_nadir_event_times)

    # convert fractional value to degrees offset [0, 180]
    degrees = position_as_percent(evts, time) * 180

    # add 180 degrees if prior event is nadir
    return degrees if evts[0].event.value else degrees + 180


def earth(time):
    eo_degrees = orbit_degrees_from_winter_solstice(time)
    er_degrees = rotation_degrees_from_solar_noon(time)
    mo_degrees = almanac.moon_phase(ephemeris, time).degrees
    return Earth(eo_degrees, er_degrees, mo_degrees)


def earth_now():
    return earth(timescale.now())


def main():
    now = timescale.now()
    em = earth(now)
    d = {
        'time': now.utc_strftime('%Y-%m-%d %H:%M:%S'),
        'earth_orbit': em.eo_degrees,
        'earth_rotation': em.er_degrees,
        'moon_orbit': em.mo_degrees,
    }
    print(d)


if __name__ == '__main__':
    main()
