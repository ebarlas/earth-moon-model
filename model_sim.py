import earth
import model
import motor
import stub


class PrintLogger:
    def info(self, message):
        print(message)


def main():
    iterations = 50
    leap = 1 / 24
    fmt = '%Y-%m-%d %H:%M:%S'
    eo_ma = stub.MotorAssembly(100, [(345, 360), (0, 15)])
    er_ma = stub.MotorAssembly(200, [(345, 360), (0, 15)])
    mo_ma = stub.MotorAssembly(300, [(345, 360), (0, 15)])
    eo_motor = motor.Motor(eo_ma, eo_ma)
    er_motor = motor.Motor(er_ma, er_ma)
    mo_motor = motor.Motor(mo_ma, mo_ma)
    logger = PrintLogger()
    em = model.Model(eo_motor, er_motor, mo_motor, logger, 360)
    em.init()
    t = earth.timescale.now()
    print(t.utc_strftime(fmt))
    em.next(earth.earth(t))
    for i in range(iterations):
        # leap = float(input())
        t += leap
        print(t.utc_strftime(fmt))
        em.next(earth.earth(t))


if __name__ == '__main__':
    main()
