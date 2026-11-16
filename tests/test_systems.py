"""sdata.system and its words, sdata.frequency_filter, checked against R.

Reference values: R 4.6.2 with control 0.2.5, signal 1.8.1, gsignal 0.3.7 and pracma 2.4.6
(ref_systems.R in the v0.6 scratch folder, partD). s1 <- control::tf(1, c(1, 2, 5)).
R control has no stepinfo and no margin: rise time, settling time, overshoot and the margins come from
python-control (step_info, stability_margins; simplydata[systems]). Their references are python-control's own
results, the examples on MATLAB's stepinfo and margin pages, and margins worked out by hand where the
formula allows.
"""

import numpy as np
import pytest

import simplydata as sdata
from simplydata import SimplydataError


def frame(table):
    return table._frame.to_pandas()


@pytest.fixture
def s1():
    return sdata.system("1 / (s**2 + 2*s + 5)")


def test_system_from_formula_prints_poles_and_gain(capsys):
    s = sdata.system("1 / (s**2 + 2*s + 5)")
    out = capsys.readouterr().out
    assert "A continuous system: output / input = 1 / (s**2 + 2*s + 5)." in out
    assert "Poles -1 +/- 2i: stable (every pole has a negative real part)." in out
    assert "Steady gain 0.2: a constant input of 1 settles at 0.2." in out
    assert "control::tf" in out
    assert "1 / (s**2 + 2*s + 5)" in repr(s)


def test_other_ways_to_make_a_system(capsys):
    a = sdata.system(numerator=[1], denominator=[1, 2, 5])
    b = sdata.system(poles=[-1, -2], gain=3)
    c = sdata.system(a=[[0, 1], [-5, -2]], b=[[0], [1]], c=[[1, 0]], d=[[0]])
    d = sdata.system("2 / (2*s**2 + 4*s + 10)")
    e = sdata.system("(s + 1)**2 / ((s + 1) * (s**2 + 2*s + 5) * (s + 1))")
    for got in (a, c, d):
        assert got._num == pytest.approx([1]) and got._den == pytest.approx([1, 2, 5])
    # R: control::zp2tf(numeric(0), c(-1, -2), 3)$den
    assert b._den == pytest.approx([1, 3, 2]) and b._num == pytest.approx([3])
    # R: control::ss2tf(...) gives 1 / (s^2 + 2 s + 5) (with a -4.4e-16 rounding term that simplydata drops)
    assert len(c._num) == 1
    assert e._den[0] == 1 and len(e._den) == 5
    assert "(s**2 + 2*s + 1) / (s**4" in capsys.readouterr().out


def test_formula_errors():
    with pytest.raises(SimplydataError, match=r"\*\*"):
        sdata.system("1 / (s^2 + 1)")
    with pytest.raises(SimplydataError, match="2\\*s, not 2s"):
        sdata.system("1 / (2s + 1)")
    with pytest.raises(SimplydataError, match='"x" is not allowed'):
        sdata.system("1 / (x + 1)")
    with pytest.raises(SimplydataError, match="give time_step="):
        sdata.system("0.1 / (z - 0.9)")
    with pytest.raises(SimplydataError, match="leave out time_step="):
        sdata.system("1 / (s + 1)", time_step=0.1)
    with pytest.raises(SimplydataError, match="improper"):
        sdata.system("s**2 / (s + 1)")
    with pytest.raises(SimplydataError, match="needs one of"):
        sdata.system()
    with pytest.raises(SimplydataError, match="one input and one output"):
        sdata.system(a=[[0, 1], [-5, -2]], b=[[0, 1], [1, 0]], c=[[1, 0]])
    with pytest.raises(SimplydataError, match="Powers must be whole numbers"):
        sdata.system("1 / (s**0.5 + 1)")


def test_step_response_matches_r(s1, capsys, needs_control):
    got = frame(s1.step_response(time_points=np.arange(0, 6.0001, 0.03)))
    # R: control::step(s1, t = seq(0, 6, by = 0.03))$y[1, c(2, 18, 201)]
    assert got["output"].to_numpy()[[1, 17, 200]] == pytest.approx(
        [0.000440968660669288, 0.0859755020493958, 0.199714662161444], rel=1e-8)
    out = capsys.readouterr().out
    # python-control: control.step_info(control.tf([1], [1, 2, 5]), T=np.arange(0, 6.0001, 0.03)):
    #    RiseTime 0.69, SettlingTime 3.75, Peak 0.24156371289887466, PeakTime 1.56, Overshoot 20.78185644943732
    #    (R control has no stepinfo; R's response above is the same, so the measures are too)
    assert "settles at 0.2, peaks at 0.2416 at time 1.56 (overshoot 20.8 %)" in out
    assert "rise time 0.69 (10 % to 90 %), settling time 3.75 (within 2 %)" in out
    assert "python-control step_info" in out
    from simplydata.systems import step_info

    info = step_info(got["time"].to_numpy(), got["output"].to_numpy(), 0.2)
    assert info["rise time"] == pytest.approx(0.69, rel=1e-12)
    assert info["settling time"] == pytest.approx(3.75, rel=1e-12)
    assert info["overshoot"] == pytest.approx(20.78185644943732, rel=1e-10)
    assert len(frame(s1.step_response(until=10))) == 200


def test_step_measures_match_matlab_stepinfo(capsys, needs_control):
    # MATLAB documentation, stepinfo, first example: sys = tf([1 5 5], [1 1.65 5 6.5 2]); S = stepinfo(sys):
    #    RiseTime 3.8456, SettlingTime 27.9762, Overshoot 7.4915, Peak 2.6873, PeakTime 8.0530
    # MATLAB interpolates on its own time grid; python-control takes the first time shown, here 0.001 apart
    h = sdata.system("(s**2 + 5*s + 5) / (s**4 + 1.65*s**3 + 5*s**2 + 6.5*s + 2)")
    got = frame(h.step_response(until=40, how_many=40001))
    from simplydata.systems import step_info

    info = step_info(got["time"].to_numpy(), got["output"].to_numpy(), 2.5)
    assert info["rise time"] == pytest.approx(3.8456, abs=0.005)
    assert info["settling time"] == pytest.approx(27.9762, abs=0.01)
    assert info["overshoot"] == pytest.approx(7.4915, abs=0.03)
    assert info["peak"] == pytest.approx(2.6873, abs=0.001)
    assert info["peak time"] == pytest.approx(8.0530, abs=0.05)


def test_step_response_time_points_start_at_zero_and_keep_the_step(capsys):
    in_steps = sdata.system("0.1 / (z - 0.9)", time_step=0.1)
    with pytest.raises(SimplydataError, match="0.1 apart, the system's time step"):
        in_steps.step_response(time_points=[0, 0.5, 1.0, 1.5])
    with pytest.raises(SimplydataError, match="start at 0"):
        in_steps.impulse_response(time_points=[0.5, 0.6, 0.7])
    got = frame(in_steps.step_response(time_points=[0, 0.1, 0.2, 0.3]))
    # R: control::step(control::tf(0.1, c(1, -0.9), 0.1), t = c(0, 0.1, 0.2, 0.3))$y: 0, 0.1, 0.19, 0.271
    assert got["output"].tolist() == pytest.approx([0, 0.1, 0.19, 0.271], rel=1e-12)
    with pytest.raises(SimplydataError, match="start at 0"):
        sdata.system("1 / (s + 1)").step_response(time_points=[5, 6, 7, 8])


def test_response_to_refuses_inputs_in_other_steps(capsys):
    in_steps = sdata.system("0.1 / (z - 0.9)", time_step=0.1)
    inputs = sdata.make_wave("sine", frequency=1, time_step=0.01, how_many=50)
    with pytest.raises(SimplydataError, match="remember a time step of 0.01, but the system works in steps of 0.1"):
        in_steps.response_to(inputs)
    inputs.change_time_step(to=0.1)
    assert len(frame(in_steps.response_to(inputs))) == 5


def test_impulse_and_response_to_match_r(s1, capsys):
    got = frame(s1.impulse_response(time_points=np.arange(0, 6.0001, 0.03)))
    # R: control::impulse(s1, t)$y[1, c(2, 18)]
    assert got["output"].to_numpy()[[1, 17]] == pytest.approx([0.0290959011308254, 0.255843549925528], rel=1e-8)
    square = sdata.make_wave("square", frequency=0.2, time_step=0.05, how_many=400)
    got = frame(s1.response_to(square))
    # R: tt <- (0:399) * 0.05; u <- gsignal::square(2 * pi * 0.2 * tt); control::lsim(s1, u, tt)$y[c(100, 400)]
    assert got["output"].to_numpy()[[99, 399]] == pytest.approx([-0.208934151094657, -0.20744338441064], rel=1e-8)
    assert list(got.columns) == ["time", "input", "output"]
    with pytest.raises(SimplydataError, match="time_points="):
        s1.response_to([1, 2, 3])
    with pytest.raises(SimplydataError, match="one time point per input"):
        s1.response_to([1, 2, 3], time_points=[0, 1])
    # the spelling before the name review still works, with a note
    old = frame(s1.impulse_response(times=np.arange(0, 6.0001, 0.03)))
    assert old["output"].to_numpy()[1] == pytest.approx(0.0290959011308254, rel=1e-8)


def test_frequency_response_matches_r(s1, capsys, needs_control):
    got = frame(s1.frequency_response(between=[0.1, 10], how_many=3))
    # R: control::bode(s1, w = c(0.1, 1, 10))$mag, $phase
    assert got["gain (decibels)"].tolist() == pytest.approx([-13.9689819049622, -13.0102999566398, -39.7428135887783],
                                                      rel=1e-10)
    assert got["phase (degrees)"].tolist() == pytest.approx([-2.29519553918841, -26.565051177078, -168.111341960372],
                                                            rel=1e-10)
    assert got["gain"].iloc[0] == pytest.approx(10 ** (-13.9689819049622 / 20), rel=1e-10)
    assert "both margins are without limit" in capsys.readouterr().out
    cycles = frame(s1.frequency_response(between=[0.1 / (2 * np.pi), 10 / (2 * np.pi)], how_many=3,
                                         unit="cycles per second"))
    assert cycles["gain (decibels)"].tolist() == pytest.approx(got["gain (decibels)"].tolist(), rel=1e-10)
    # the spellings before the name review (steps=, units=, "hertz") still work
    hertz = frame(s1.frequency_response(between=[0.1 / (2 * np.pi), 10 / (2 * np.pi)], steps=3, units="hertz"))
    assert hertz["gain (decibels)"].tolist() == pytest.approx(got["gain (decibels)"].tolist(), rel=1e-10)


def test_margins_match_r(capsys, needs_control):
    loop = sdata.system("4 / (s * (s + 1) * (s + 2))")
    gm, wg, pm, wp = loop._margins()
    # by hand: the phase is -180 degrees at w = sqrt(2), where |L| = 4 / (sqrt(2) sqrt(3) sqrt(6)) = 2/3, so the
    #    gain margin is 20 log10(3/2) = 3.52182518111363 dB; python-control stability_margins(L): phase margin
    #    11.424981844921433 degrees at 1.1432030439610739 (R: uniroot on control::freqresp(L, w) gives the same)
    assert gm == pytest.approx(20 * np.log10(1.5), rel=1e-10) and wg == pytest.approx(np.sqrt(2), rel=1e-10)
    assert pm == pytest.approx(11.424981844921433, rel=1e-8) and wp == pytest.approx(1.1432030439610739, rel=1e-8)
    loop.frequency_response()
    out = capsys.readouterr().out
    assert "gain margin 3.52 decibels at 1.414 radians per second; phase margin 11.42 degrees at 1.143" in out
    assert "not stable (a pole lies on the imaginary axis" in out


def test_poles_zeros_stability_gain(s1, capsys):
    got = frame(s1.poles())
    # R: control::pole(s1); control::damp(s1)$zeta, $omegan
    assert sorted(got["imaginary part"]) == pytest.approx([-2, 2])
    assert got["real part"].tolist() == pytest.approx([-1, -1])
    assert got["distance from 0"].tolist() == pytest.approx([5 ** 0.5] * 2, rel=1e-12)  # R: Mod(control::pole(s1))
    assert got["damping ratio"].tolist() == pytest.approx([0.447213595499958] * 2, rel=1e-12)
    assert got["natural frequency"].tolist() == pytest.approx([5 ** 0.5] * 2, rel=1e-12)
    assert len(frame(s1.zeros())) == 0
    assert s1.is_stable() is True
    assert s1.steady_gain() == pytest.approx(0.2)  # R: control::dcgain(s1)
    assert sdata.system("1 / (s - 1)").is_stable() is False
    assert sdata.system("1 / (s**2 + 4)").is_stable() is False
    assert np.isinf(sdata.system("1 / (s * (s + 1))").steady_gain())
    out = capsys.readouterr().out
    assert "positive real part" in out and "imaginary axis" in out and "without limit" in out


def test_in_steps_matches_r(s1, capsys):
    zoh = s1.in_steps(time_step=0.1)
    # R: control::c2d(s1, 0.1)$num, $den
    assert zoh._num == pytest.approx([0.00466347320860461, 0.00436231268810872], rel=1e-9)
    assert zoh._den == pytest.approx([1, -1.77360182359442, 0.818730753077982], rel=1e-12)
    assert "z**2 - 1.7736*z + 0.818731" in capsys.readouterr().out
    tustin = s1.in_steps(time_step=0.1, method="tustin")
    # R: signal::bilinear(numeric(0), control::pole(s1), 1, 0.1), as.Arma, divided by a[1]
    assert tustin._num == pytest.approx([0.00224719101123596, 0.00449438202247191, 0.00224719101123596], rel=1e-10)
    assert tustin._den == pytest.approx([1, -1.7752808988764, 0.820224719101123], rel=1e-10)
    # R: s = (z - 1) / T and s = (z - 1) / (z T) put into 1 / (s^2 + 2 s + 5) (ref_systems.R)
    euler = s1.in_steps(time_step=0.1, method="forward difference")
    assert euler._den == pytest.approx([1, -1.8, 0.85]) and euler._num == pytest.approx([0.01])
    back = s1.in_steps(time_step=0.1, method="backward difference")
    assert back._den == pytest.approx([1, -1.76, 0.8]) and back._num == pytest.approx([0.008, 0, 0])
    with pytest.raises(SimplydataError, match="already in steps"):
        zoh.in_steps(time_step=0.1)
    with pytest.raises(SimplydataError, match="method"):
        s1.in_steps(time_step=0.1, method="magic")


def test_joining_systems_matches_r(s1, capsys):
    other = sdata.system("(s + 1) / (s + 3)")
    assert s1.with_feedback()._den == pytest.approx([1, 2, 6])  # R: control::feedback(s1, 1)$den
    joined = s1.then(other)  # R: control::series(s1, tf(c(1, 1), c(1, 3)))
    assert joined._num == pytest.approx([1, 1]) and joined._den == pytest.approx([1, 5, 11, 15])
    both = s1.add(sdata.system("(s + 1) / (s**2 + 3*s + 2)"))
    # R by hand (control::parallel fails when the orders differ): pracma::polyadd(polymul(...), ...)
    assert both._num == pytest.approx([1, 4, 10, 7]) and both._den == pytest.approx([1, 5, 13, 19, 10])
    assert s1.with_feedback(sign="positive")._den == pytest.approx([1, 2, 4])
    assert s1.with_feedback(2)._den == pytest.approx([1, 2, 7])
    assert s1.with_feedback(through=2)._den == pytest.approx([1, 2, 7])
    assert s1.with_feedback(other=2)._den == pytest.approx([1, 2, 7])  # the spelling before the name review
    assert "Side by side, outputs added (in parallel)" in capsys.readouterr().out
    with pytest.raises(SimplydataError, match="same kind"):
        s1.then(s1.in_steps(time_step=0.1))


def test_tables_of_a_system(s1):
    tf = frame(s1.table())
    assert tf["power of s"].tolist() == [2, 1, 0] and tf["denominator"].tolist() == [1, 2, 5]
    assert tf["numerator"].tolist() == [0, 0, 1]
    ss = frame(s1.table(form="state space"))
    # R: control::tf2ss(s1): A = [-2 -5; 1 0], B = [1; 0], C = [0 1]
    assert ss[ss["matrix"] == "A"]["value"].tolist() == pytest.approx([-2, -5, 1, 0])
    assert ss[ss["matrix"] == "B"]["value"].tolist() == pytest.approx([1, 0])
    assert ss[ss["matrix"] == "C"]["value"].tolist() == pytest.approx([0, 1])
    pz = frame(s1.table(form="poles and zeros"))
    assert pz["kind"].tolist() == ["pole", "pole", "gain"]
    assert pz["real part"].tolist() == pytest.approx([-1, -1, 1])
    assert sorted(pz["imaginary part"]) == pytest.approx([-2, 0, 2])
    assert frame(s1.in_steps(time_step=0.1).table()).columns[0] == "power of z"


def test_system_in_steps_matches_r(capsys):
    d = sdata.system("0.1 / (z - 0.9)", time_step=0.1)
    assert "every pole lies inside the unit circle: its distance from 0 is below 1" in capsys.readouterr().out
    # R: signal::filter(c(0, 0.1), c(1, -0.9), rep(1, 5))
    assert frame(d.step_response(how_many=5))["output"].tolist() == pytest.approx([0, 0.1, 0.19, 0.271, 0.3439])
    got = frame(d.frequency_response(between=[0.1, 10], how_many=3))
    # R: H(exp(1i * w * 0.1)) with pracma::polyval: 20 * log10(Mod(h)), Arg(h) * 180 / pi
    assert got["gain (decibels)"].tolist() == pytest.approx([-0.038911339554644, -2.78582192232688, -19.2296192036422],
                                                      rel=1e-10)
    assert got["phase (degrees)"].tolist() == pytest.approx([-5.71333635003828, -46.4198445563431,
                                                             -113.144914437539], rel=1e-10)
    # R: Mod(log(0.9 + 0i) / 0.1) (as control::damp for a system in steps)
    assert frame(d.poles())["natural frequency"].tolist() == pytest.approx([1.05360515657826], rel=1e-12)
    with pytest.raises(SimplydataError, match="highest frequency"):
        d.frequency_response(between=[1, 100])


def test_frequency_filter_matches_r(capsys):
    f = sdata.frequency_filter(keep_below=10, time_step=0.005)
    out = capsys.readouterr().out
    assert "The filter that keeps the frequencies below 10 (Butterworth filter, steepness 4)" in out
    assert "signal::butter(4, 0.1)" in out
    got = frame(f.frequency_response(between=[1, 50], how_many=3))
    # R: bw <- signal::butter(4, 0.1); Mod(H(c(1, 10, 50))) with H from pracma::polyval at exp(2i pi f 0.005)
    assert got["frequency"].tolist() == pytest.approx([1, 50 ** 0.5, 50])
    one = frame(f.frequency_response(between=[1, 10], how_many=2))
    assert one["gain"].tolist() == pytest.approx([0.999999995317016, 0.707106781186491], rel=1e-9)
    assert one["phase (degrees)"].iloc[0] == pytest.approx(-14.8702778963188, rel=1e-9)
    assert "Margins" not in capsys.readouterr().out
    # R: signal::filter(bw, rep(1, 30))[c(10, 30)]
    assert frame(f.step_response(how_many=30))["output"].to_numpy()[[9, 29]] == pytest.approx(
        [0.566482373425294, 0.970650951681188], rel=1e-9)
    assert len(frame(f.poles())) == 4 and f.is_stable()
    notch = sdata.frequency_filter(remove_at=50, time_step=0.005)
    assert "The notch filter at 50" in repr(notch)
    with pytest.raises(SimplydataError, match="exactly one"):
        sdata.frequency_filter(time_step=0.005)


def test_system_charts(s1, tmp_path):
    import matplotlib

    matplotlib.use("Agg")
    bode = s1.chart(between=[0.1, 10])
    fig = bode._render()
    axes = [ax for sub in fig.subfigs for ax in sub.axes]
    assert len(axes) == 2 and axes[0].get_xscale() == "log"
    step = s1.chart(show="step", until=6)
    line = step._render().axes[0].get_lines()[0]
    assert line.get_xdata()[-1] == pytest.approx(6)
    assert line.get_ydata()[-1] == pytest.approx(frame(s1.step_response(until=6))["output"].iloc[-1])
    pz = s1.chart(show="poles and zeros")._render().axes[0]
    offsets = pz.collections[0].get_offsets()
    assert sorted(offsets[:, 1]) == pytest.approx([-2, 2])
    assert pz.get_xlabel() == "real part" and pz.get_ylabel() == "imaginary part"
    nyquist = s1.chart(show="nyquist")._render().axes[0]
    assert nyquist.get_lines()[0].get_xdata()[0] == pytest.approx(0.2, rel=1e-3)
    s1.chart(show="impulse").save(str(tmp_path / "impulse.png"))
    s1.in_steps(time_step=0.1).chart(show="pole-zero").save(str(tmp_path / "pz.png"))  # accepted spelling
    s1.chart(unit="cycles per second")._render()
    with pytest.raises(SimplydataError, match="show"):
        s1.chart(show="sideways")
    with pytest.raises(SimplydataError, match='between= goes with show="bode"'):
        s1.chart(show="step", between=[0.1, 10])
    with pytest.raises(SimplydataError, match="until= goes with"):
        s1.chart(show="nyquist", until=5)
    with pytest.raises(SimplydataError, match="unit= goes with"):
        s1.chart(show="poles and zeros", unit="hertz")


def test_other_names_on_a_system(s1):
    with pytest.raises(AttributeError, match="frequency_response"):
        s1.bode()
    with pytest.raises(AttributeError, match="with_feedback"):
        s1.feedback()
    with pytest.raises(AttributeError, match="Did you mean .poles()"):
        s1.polls()
    with pytest.raises(AttributeError, match="A system has no word called .stepinfo"):
        s1.stepinfo()


def test_two_spellings_of_one_option_are_refused():
    with pytest.raises(SimplydataError, match="numerator= or num="):
        sdata.system(numerator=[1], num=[1], denominator=[1, 2, 5])
    with pytest.raises(SimplydataError, match="a= or A="):
        sdata.system(a=[[0, 1], [-5, -2]], A=[[0, 1], [-5, -2]], b=[[0], [1]], c=[[1, 0]])
    assert sdata.system(num=[1], den=[1, 2, 5])._den == pytest.approx([1, 2, 5])


def test_gain_is_explained(capsys):
    sdata.system(poles=[-1, -2], gain=2)
    # R: control::dcgain(control::zpk(NULL, c(-1, -2), 2)) is 1
    assert "gain=2 is the number in front of the formula; the steady gain is 1." in capsys.readouterr().out


def test_margins_match_matlab_margin(capsys, needs_control):
    # MATLAB documentation, margin: sys = tf(1, [1 2 1 0]) has Gm 6.02 dB, Pm 21.4 deg; by hand the phase is
    #    -180 degrees at w = 1, where |L| = 1/2, so Gm = 2 (6.0206 dB) at 1
    gm, wg, pm, wp = sdata.system("1 / (s**3 + 2*s**2 + s)")._margins()
    assert gm == pytest.approx(20 * np.log10(2), rel=1e-10) and wg == pytest.approx(1, rel=1e-10)
    assert pm == pytest.approx(21.4, abs=0.05)
    # MATLAB documentation, margin, a system in steps: tf([0.04798 0.0464], [1 -1.81 0.9048], 0.1):
    #    Gm 2.0519 (6.2427 dB), Pm 13.5711, Wcg 5.4376, Wcp 4.3544
    d = sdata.system(numerator=[0.04798, 0.0464], denominator=[1, -1.81, 0.9048], time_step=0.1)
    gm, wg, pm, wp = d._margins()
    # (python-control: Gm 2.05172 at 5.43741; MATLAB shows 2.0519 at 5.4376, within 1e-4 of their size)
    assert 10 ** (gm / 20) == pytest.approx(2.0519, rel=2e-4) and wg == pytest.approx(5.4376, rel=1e-4)
    assert pm == pytest.approx(13.5711, abs=1e-4) and wp == pytest.approx(4.3544, abs=1e-4)


def test_without_python_control_the_responses_still_come(s1, capsys, monkeypatch):
    import sys

    monkeypatch.setitem(sys.modules, "control", None)  # import control now fails, as when it is not installed
    got = frame(s1.step_response(until=6))
    assert len(got) == 200
    out = capsys.readouterr().out
    assert "Step response: the output settles at 0.2." in out
    assert 'Rise time, settling time and overshoot come from python-control' in out
    assert 'pip install "simplydata[systems]"' in out
    sdata.system("4 / (s * (s + 1) * (s + 2))").frequency_response()
    assert "The gain and phase margins come from python-control" in capsys.readouterr().out
