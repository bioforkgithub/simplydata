"""sdata.system and its words, sdata.frequency_filter, checked against R.

Reference values: R 4.6.2 with control 0.2.5, signal 1.8.1, gsignal 0.3.7 and pracma 2.4.6
(ref_systems.R in the v0.6 scratch folder, partD). s1 <- control::tf(1, c(1, 2, 5)).
R control has no stepinfo and no margin: rise time, settling time, overshoot and the margins are worked
out in R from R's own responses (uniroot for the margins), by the same rules simplydata states.
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


def test_step_response_matches_r(s1, capsys):
    got = frame(s1.step_response(times=np.arange(0, 6.0001, 0.03)))
    # R: control::step(s1, t = seq(0, 6, by = 0.03))$y[1, c(2, 18, 201)]
    assert got["output"].to_numpy()[[1, 17, 200]] == pytest.approx(
        [0.000440968660669288, 0.0859755020493958, 0.199714662161444], rel=1e-8)
    out = capsys.readouterr().out
    # R: from the same response: rise 0.689562487797941, settling 3.73521350733359, peak 0.241563712898874 at
    #    1.56, overshoot 20.7818564494371 %
    assert "settles at 0.2, peaks at 0.2416 at time 1.56 (overshoot 20.8 %)" in out
    assert "rise time 0.6896 (10 % to 90 %), settling time 3.735 (within 2 %)" in out
    from simplydata.systems import step_info

    info = step_info(got["time"].to_numpy(), got["output"].to_numpy(), 0.2)
    assert info["rise time"] == pytest.approx(0.689562487797941, rel=1e-6)
    assert info["settling time"] == pytest.approx(3.73521350733359, rel=1e-6)
    assert info["overshoot"] == pytest.approx(20.7818564494371, rel=1e-6)
    assert len(frame(s1.step_response(until=10))) == 200


def test_impulse_and_response_to_match_r(s1, capsys):
    got = frame(s1.impulse_response(times=np.arange(0, 6.0001, 0.03)))
    # R: control::impulse(s1, t)$y[1, c(2, 18)]
    assert got["output"].to_numpy()[[1, 17]] == pytest.approx([0.0290959011308254, 0.255843549925528], rel=1e-8)
    square = sdata.wave("square", frequency=0.2, time_step=0.05, how_many=400)
    got = frame(s1.response_to(square))
    # R: tt <- (0:399) * 0.05; u <- gsignal::square(2 * pi * 0.2 * tt); control::lsim(s1, u, tt)$y[c(100, 400)]
    assert got["output"].to_numpy()[[99, 399]] == pytest.approx([-0.208934151094657, -0.20744338441064], rel=1e-8)
    assert list(got.columns) == ["time", "input", "output"]
    with pytest.raises(SimplydataError, match="times="):
        s1.response_to([1, 2, 3])
    with pytest.raises(SimplydataError, match="one time per input"):
        s1.response_to([1, 2, 3], times=[0, 1])


def test_frequency_response_matches_r(s1, capsys):
    got = frame(s1.frequency_response(between=[0.1, 10], steps=3))
    # R: control::bode(s1, w = c(0.1, 1, 10))$mag, $phase
    assert got["gain (dB)"].tolist() == pytest.approx([-13.9689819049622, -13.0102999566398, -39.7428135887783],
                                                      rel=1e-10)
    assert got["phase (degrees)"].tolist() == pytest.approx([-2.29519553918841, -26.565051177078, -168.111341960372],
                                                            rel=1e-10)
    assert got["gain"].iloc[0] == pytest.approx(10 ** (-13.9689819049622 / 20), rel=1e-10)
    assert "both margins are without limit" in capsys.readouterr().out
    hertz = frame(s1.frequency_response(between=[0.1 / (2 * np.pi), 10 / (2 * np.pi)], steps=3, units="hertz"))
    assert hertz["gain (dB)"].tolist() == pytest.approx(got["gain (dB)"].tolist(), rel=1e-10)


def test_margins_match_r(capsys):
    loop = sdata.system("4 / (s * (s + 1) * (s + 2))")
    gm, wg, pm, wp = loop._margins()
    # R: uniroot on control::freqresp(L, w): phase margin 11.4249818449277 degrees at 1.14320304396094;
    #    gain margin 3.52182518111363 dB at 1.4142135623731
    assert pm == pytest.approx(11.4249818449277, abs=1e-3) and wp == pytest.approx(1.14320304396094, rel=1e-5)
    assert gm == pytest.approx(3.52182518111363, abs=1e-5) and wg == pytest.approx(1.4142135623731, rel=1e-5)
    loop.frequency_response()
    out = capsys.readouterr().out
    assert "gain margin 3.52 dB at 1.414 radians per second; phase margin 11.42 degrees at 1.143" in out
    assert "not stable (a pole lies on the imaginary axis" in out


def test_poles_zeros_stability_gain(s1, capsys):
    got = frame(s1.poles())
    # R: control::pole(s1); control::damp(s1)$zeta, $omegan
    assert sorted(got["imaginary"]) == pytest.approx([-2, 2]) and got["real"].tolist() == pytest.approx([-1, -1])
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
    with pytest.raises(SimplydataError, match="same kind"):
        s1.then(s1.in_steps(time_step=0.1))


def test_tables_of_a_system(s1):
    tf = frame(s1.table())
    assert tf["power"].tolist() == [2, 1, 0] and tf["denominator"].tolist() == [1, 2, 5]
    assert tf["numerator"].tolist() == [0, 0, 1]
    ss = frame(s1.table(form="state space"))
    # R: control::tf2ss(s1): A = [-2 -5; 1 0], B = [1; 0], C = [0 1]
    assert ss[ss["matrix"] == "A"]["value"].tolist() == pytest.approx([-2, -5, 1, 0])
    assert ss[ss["matrix"] == "B"]["value"].tolist() == pytest.approx([1, 0])
    assert ss[ss["matrix"] == "C"]["value"].tolist() == pytest.approx([0, 1])
    pz = frame(s1.table(form="poles and zeros"))
    assert pz["kind"].tolist() == ["pole", "pole", "gain"]


def test_system_in_steps_matches_r(capsys):
    d = sdata.system("0.1 / (z - 0.9)", time_step=0.1)
    assert "every pole has a size below 1" in capsys.readouterr().out
    # R: signal::filter(c(0, 0.1), c(1, -0.9), rep(1, 5))
    assert frame(d.step_response(steps=5))["output"].tolist() == pytest.approx([0, 0.1, 0.19, 0.271, 0.3439])
    got = frame(d.frequency_response(between=[0.1, 10], steps=3))
    # R: H(exp(1i * w * 0.1)) with pracma::polyval: 20 * log10(Mod(h)), Arg(h) * 180 / pi
    assert got["gain (dB)"].tolist() == pytest.approx([-0.038911339554644, -2.78582192232688, -19.2296192036422],
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
    got = frame(f.frequency_response(between=[1, 50], steps=3))
    # R: bw <- signal::butter(4, 0.1); Mod(H(c(1, 10, 50))) with H from pracma::polyval at exp(2i pi f 0.005)
    assert got["frequency"].tolist() == pytest.approx([1, 50 ** 0.5, 50])
    one = frame(f.frequency_response(between=[1, 10], steps=2))
    assert one["gain"].tolist() == pytest.approx([0.999999995317016, 0.707106781186491], rel=1e-9)
    assert one["phase (degrees)"].iloc[0] == pytest.approx(-14.8702778963188, rel=1e-9)
    assert "Margins" not in capsys.readouterr().out
    # R: signal::filter(bw, rep(1, 30))[c(10, 30)]
    assert frame(f.step_response(steps=30))["output"].to_numpy()[[9, 29]] == pytest.approx(
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
    pz = s1.chart(show="pole-zero")._render().axes[0]
    offsets = pz.collections[0].get_offsets()
    assert sorted(offsets[:, 1]) == pytest.approx([-2, 2])
    nyquist = s1.chart(show="nyquist")._render().axes[0]
    assert nyquist.get_lines()[0].get_xdata()[0] == pytest.approx(0.2, rel=1e-3)
    s1.chart(show="impulse").save(str(tmp_path / "impulse.png"))
    s1.in_steps(time_step=0.1).chart(show="pole-zero").save(str(tmp_path / "pz.png"))
    with pytest.raises(SimplydataError, match="show"):
        s1.chart(show="sideways")


def test_other_names_on_a_system(s1):
    with pytest.raises(AttributeError, match="frequency_response"):
        s1.bode()
    with pytest.raises(AttributeError, match="with_feedback"):
        s1.feedback()
    with pytest.raises(AttributeError, match="Did you mean .poles()"):
        s1.polls()
