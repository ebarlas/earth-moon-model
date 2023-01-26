import unittest

from steps import Steps


class TestSteps(unittest.TestCase):

    def test_steps(self):
        s = Steps(steps=20)
        self.assertEqual((True, 20), s.get())
        s.add(5, False)
        self.assertEqual((True, 15), s.get())
        s.add(-5)
        self.assertEqual((True, 10), s.get())
        s.add(-20)
        self.assertEqual((False, 10), s.get())
        s.add(-190)
        self.assertEqual((True, 0), s.get())

    def test_degrees(self):
        s = Steps(degrees=180)
        self.assertEqual((True, 100), s.get())
        s.add_degrees(-90)
        self.assertEqual((True, 50), s.get())
        s.add_degrees(-180)
        self.assertEqual((False, 50), s.get())

    def test_reverse(self):
        s = Steps(steps=-30)
        self.assertEqual((False, 30), s.get())
        self.assertEqual((True, 30), s.reverse().get())

    def test_equality(self):
        self.assertEqual(Steps(steps=10), Steps(steps=10))
        self.assertNotEqual(Steps(steps=10), Steps(steps=11))
        self.assertEqual(Steps(steps=10), Steps(steps=-190))


if __name__ == '__main__':
    unittest.main()
