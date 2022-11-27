import unittest
from datetime import datetime

from skyfield import api

import earth

timescale = api.load.timescale()


class TestEarth(unittest.TestCase):

    def test_summer_solstice(self):
        # summer solstice at 9:13 AM UTC on June 21, 2022
        dt = datetime.fromisoformat('2022-06-21T09:13:00+00:00')
        ts = timescale.from_datetime(dt)
        em = earth.earth_model(ts)
        self.assertTrue(abs(round(em.earth_orbit_degrees)) == 180) # allow -180 or 180

        # 3:43 AM UTC sunrise and 8:21 PM UTC sunset in London on 6/20
        # 3:43 AM UTC sunrise and 8:22 PM UTC sunset in London on 6/21
        #
        # 3:43 AM (6/21 sunrise) - 8:21 PM (6/20 sunset) = 7h 22m, half is 3h 41m
        # nadir is at 8:21 PM (6/20 sunset) + 3:41 = 12:02 AM on 6/21
        #
        # 8:22 PM (6/21 sunset) - 3:43 AM (6/21 sunrise) = 16h 39m, half is 8m 20m
        # solar noon is at 3:43 AM (6/21 sunrise) + 8:20 = 12:03 PM on 6/21
        #
        # 12:03 PM - 12:02 AM = 12h 1m = 721 minutes between nadir and solar noon
        # 9:13 AM (target time) - 12:02 AM = 9h 11m = 551 minutes
        # 551 / 721 = 0.764 = 137.559 degrees of rotation from nadir and 317.559 degrees from solar noon
        self.assertAlmostEqual(317.559, em.earth_rotation_degrees, delta=1.0)


if __name__ == '__main__':
    unittest.main()
