import re
import sys
import os


def extract_numbers(s: str) -> list[int]:
    """
    >>> extract_numbers('9min @ 85rpm, from 88 to 95% FTP')
    [9, 85, 88, 95]

    >>> extract_numbers('8min from 50 to 80% FTP')
    [8, 50, 80]

    >>> extract_numbers('8min 10sec from 50 to 80% FTP')
    [8, 10, 50, 80]
    """
    p = re.compile("[0-9]+")  # all numbers in string
    m = p.findall(s)

    return [int(n) for n in m]


def convert_ramp_to_mrc(ramp: str, time_per_unit=0.5) -> list[list[float, float]]:
    """
    >>> convert_ramp_to_mrc('9min @ 85rpm, from 88 to 95% FTP')
    [[0, 88], [0.5, 88.38888888888889], [1.0, 88.77777777777777], [1.5, 89.16666666666666], [2.0, 89.55555555555554], [2.5, 89.94444444444443], [3.0, 90.33333333333331], [3.5, 90.7222222222222], [4.0, 91.11111111111109], [4.5, 91.49999999999997], [5.0, 91.88888888888886], [5.5, 92.27777777777774], [6.0, 92.66666666666663], [6.5, 93.05555555555551], [7.0, 93.4444444444444], [7.5, 93.83333333333329], [8.0, 94.22222222222217], [8.5, 94.61111111111106], [9, 95]]

    >>> convert_ramp_to_mrc('8min from 50 to 80% FTP')
    [[0, 50], [0.5, 51.875], [1.0, 53.75], [1.5, 55.625], [2.0, 57.5], [2.5, 59.375], [3.0, 61.25], [3.5, 63.125], [4.0, 65.0], [4.5, 66.875], [5.0, 68.75], [5.5, 70.625], [6.0, 72.5], [6.5, 74.375], [7.0, 76.25], [7.5, 78.125], [8, 80]]

    >>> convert_ramp_to_mrc('8min 10sec from 50 to 80% FTP')
    [[0, 50], [0.5, 51.875], [1.0, 53.75], [1.5, 55.625], [2.0, 57.5], [2.5, 59.375], [3.0, 61.25], [3.5, 63.125], [4.0, 65.0], [4.5, 66.875], [5.0, 68.75], [5.5, 70.625], [6.0, 72.5], [6.5, 74.375], [7.0, 76.25], [7.5, 78.125], [8.166666666666666, 80]]
    """
    n = extract_numbers(ramp)

    duration_min = 0

    if "min" in ramp:
        duration_min += n.pop(0)

    if "sec" in ramp:
        duration_min += n.pop(0) / 60

    if "rpm" in ramp:
        n.pop(0)

    start_ftp = n.pop(0)
    end_ftp = n.pop(0)

    units = round(duration_min / time_per_unit)
    ftp_per_unit = (end_ftp - start_ftp) / units

    data = []

    time = 0
    ftp = start_ftp
    for i in range(0, units):
        if (ftp_per_unit > 0 and ftp + ftp_per_unit < end_ftp) or (
            ftp_per_unit < 0 and ftp - ftp_per_unit > end_ftp
        ):
            data.append([time_per_unit, ftp])
            ftp += ftp_per_unit
            time += time_per_unit

    data.append([duration_min - time, end_ftp])
    return data


def convert_steady_to_mrc(steady: str) -> list[list[float, float]]:
    """
    >>> convert_steady_to_mrc('2min @ 55% FTP')
    [[2, 55]]

    >>> convert_steady_to_mrc('2x 1min @ 55% FTP, 2min @ 100% FTP')
    [[1, 55], [2, 100], [1, 55], [2, 100]]
    """
    n = extract_numbers(steady)

    duration_min = 0
    repeat = 1

    if "x" in steady:
        repeat = n.pop(0)
        parts = steady.split("x")[1].split(",")
        l = []
        for i in range(repeat):
            l += convert_steady_to_mrc(parts[0])
            l += convert_steady_to_mrc(parts[1])
        return l

    if "min" in steady:
        duration_min += n.pop(0)

    if "sec" in steady:
        duration_min += n.pop(0) / 60

    if "free ride" in steady:
        return [[duration_min, 0]]

    if "rpm" in steady:
        n.pop(0)

    ftp = n.pop(0)

    return [[duration_min, ftp]]


def detect_type(line: str) -> str:
    """
    >>> detect_type('9min @ 85rpm, from 88 to 95% FTP')
    'ramp'
    >>> detect_type('2min @ 55% FTP')
    'steady'
    """
    if "from" in line:
        return "ramp"

    else:
        return "steady"


def construct(name: str, woz_data: list[str], time_per_unit=0.5) -> list[str]:
    """
    >>> construct('hi', ['9min @ 85rpm, from 88 to 95% FTP', '1min @ 85rpm, 55% FTP'])
    ['[COURSE HEADER]', 'VERSION = 2', 'UNITS = ENGLISH', 'FILE NAME = hi.mrc', 'MINUTES PERCENT', '[END COURSE HEADER]', '[COURSE DATA]', '0.00\t88.00', '0.50\t88.00', '0.50\t88.39', '1.00\t88.39', '1.00\t88.78', '1.50\t88.78', '1.50\t89.17', '2.00\t89.17', '2.00\t89.56', '2.50\t89.56', '2.50\t89.94', '3.00\t89.94', '3.00\t90.33', '3.50\t90.33', '3.50\t90.72', '4.00\t90.72', '4.00\t91.11', '4.50\t91.11', '4.50\t91.50', '5.00\t91.50', '5.00\t91.89', '5.50\t91.89', '5.50\t92.28', '6.00\t92.28', '6.00\t92.67', '6.50\t92.67', '6.50\t93.06', '7.00\t93.06', '7.00\t93.44', '7.50\t93.44', '7.50\t93.83', '8.00\t93.83', '8.00\t94.22', '8.50\t94.22', '8.50\t94.61', '9.00\t94.61', '9.00\t95.00', '10.00\t95.00', '[END COURSE DATA]']
    """
    data = []

    for d in woz_data:
        t = detect_type(d)
        if t == "steady":
            data += convert_steady_to_mrc(d)
        else:
            data += convert_ramp_to_mrc(d, time_per_unit=time_per_unit)

    course_data = [f"0.00\t{data[0][1]}"]
    last_d = None

    for d in data:

        if last_d:
            d[0] += last_d[0]
            course_data.append(f"{last_d[0]:.2f}\t{d[1]:.2f}")
        course_data.append(f"{d[0]:.2f}\t{d[1]:.2f}")

        last_d = d

    return (
        [
            "[COURSE HEADER]",
            "VERSION = 2",
            "UNITS = ENGLISH",
            f"FILE NAME = {name}.mrc",
            "MINUTES PERCENT",
            "[END COURSE HEADER]",
            "[COURSE DATA]",
        ]
        + course_data[:-1]
        + ["[END COURSE DATA]"]
    )


if __name__ == "__main__":
    if len(sys.argv) == 1:
        import doctest

        doctest.testmod()
    else:
        file_path = sys.argv[1]
        time_per_unit = 0.5
        if len(sys.argv) > 2:
            time_per_unit = int(sys.argv[2])

        with open(file_path, "r") as r:
            file_name = os.path.basename(file_path)
            dir_name = os.path.dirname(file_path)
            t = r.read().replace(",\n", ",").split("\n")
            data = construct(file_name, t, time_per_unit=time_per_unit)
            with open(f"{os.path.join(dir_name, file_name)}.mrc", "w") as f:
                f.write("\n".join(data))
