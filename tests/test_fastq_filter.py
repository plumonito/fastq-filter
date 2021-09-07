# Copyright (c) 2021 Leiden University Medical Center
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import array
import math
import statistics
from typing import List

from fastq_filter import DEFAULT_PHRED_SCORE_OFFSET, mean_quality_filter, \
    median_quality_filter, max_length_filter, min_length_filter, qualmean, \
    qualmedian, FastqRecord

import pytest  # type: ignore


def quallist_to_bytes(quallist: List[int]):
    return array.array(
        "B", [qual + DEFAULT_PHRED_SCORE_OFFSET for qual in quallist]
    ).tobytes()


QUAL_STRINGS = [
    b"I?>DC:>@?IDC9??G?>EH9E@66=9<?@E?DC:@<@BBFG>=FIC@F9>7CG?IC?I;CD9>>>A@C7>>"
    b"8>>D9GCB<;?DD>C;9?>5G>?H?=6@>:G6B<?==A7?@???8IF<75C=@A:BEA@A;C89D:=1?=<A"
    b">D=>B66C",
    b"C:@?;8@=DC???>E>E;98BBB?9D=?@B;D?I:??FD8CH?A7?<H>ABD@C@C?>;;B<><;9@8BAFD"
    b"?;:>I3DB<?<B=?A??CI>2E>><BD?A??FCBCE?DAI><B:8D>?C>@BA=F<>7=E=?DC=@9GG=>?"
    b"C@><CA;>",
]


@pytest.mark.parametrize("qualstring", QUAL_STRINGS)
def test_qualmean(qualstring):
    offset = DEFAULT_PHRED_SCORE_OFFSET
    qualities = [qual - offset for qual in array.array("b", qualstring)]
    probabilities = [10 ** (qual / -10) for qual in qualities]
    average_prob = statistics.mean(probabilities)
    phred = - 10 * math.log10(average_prob)
    assert phred == pytest.approx(qualmean(qualstring))


@pytest.mark.parametrize("qualstring", QUAL_STRINGS)
def test_qualmedian(qualstring):
    offset = DEFAULT_PHRED_SCORE_OFFSET
    qualities = [qual - offset for qual in array.array("b", qualstring)]
    median_quality = statistics.median(qualities)
    assert median_quality == pytest.approx(qualmedian(qualstring))


def test_min_length_filter_pass():
    assert min_length_filter(
        10, FastqRecord(b"", b"0123456789A", b"", b"")) is True


def test_min_length_filter_fail():
    assert min_length_filter(
        12, FastqRecord(b"", b"0123456789A", b"", b"")) is False


def test_max_length_filter_pass():
    assert max_length_filter(
        12, FastqRecord(b"", b"0123456789A", b"", b"")) is True


def test_max_length_filter_fail():
    assert max_length_filter(
        10, FastqRecord(b"", b"0123456789A", b"", b"")) is False


def test_mean_quality_filter_fail():
    assert mean_quality_filter(
        10, FastqRecord(b"", b"", b"", quallist_to_bytes([9, 9, 9]))) is False


def test_mean_quality_filter_pass():
    assert mean_quality_filter(
        8, FastqRecord(b"", b"", b"", quallist_to_bytes([9, 9, 9]))) is True

def test_median_quality_filter_fail():
    assert median_quality_filter(
        10, FastqRecord(b"", b"", b"", quallist_to_bytes([9, 9, 9, 10, 10]))
    ) is False


def test_median_quality_filter_pass():
    assert median_quality_filter(
        8-0.001, FastqRecord(b"", b"", b"", quallist_to_bytes([1, 1, 1, 8, 9, 9, 9]))
    ) is True
