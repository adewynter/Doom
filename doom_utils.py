from glob import glob


def calculate_pmat_dmat(numbers, deaths, lam=1000):
    """
    Compute PMAT and D-PMAT for a segment of a map over multiple runs.


    Parameters:
        numbers (List[int]): A list of durations (time spent in a given segment). Must be the same size as deaths.
        deaths (List[int]): A binary list (0 if no death in the run, 1 if there was one). Must be the same size as durations.
        lam (int, 1000): the weight factor for D-PMAT (default: 1000, same as our timeout)
    """
    assert len(numbers) == len(deaths)
    print("PMAT:", round(sum(numbers)/len(numbers)))
    print("D-PMAT:", round(sum([e + d*lam for e, d in zip(numbers, deaths)])/len(numbers)))


def get_fps(filedir, date=None):
    """
    Compute frames per second for a run of Doom, e.g get_fps('outputs/human_run/', date=None)

    Parameters:
        filedir (str): a path to where your frames are.
        date (str, None): a common root that needs to be removed, e.g. "2024-03-01 11". Not necessary at all
    """

    def get_vals(this_f):
        this_f = this_f.replace("\\", "/") # I swear MS' weird file conventions are annoying af
        frame_no = this_f.replace(filedir, "").split("_")[0]
        if date is None:
            _f = this_f.split(" ")[-1]
        else:
            _f = this_f.replace(date, "")
        ts = _f.replace(".png", "").strip()
        hour, minute, second, millisecond = ts.split(".")
        return frame_no, minute, second, millisecond

    files = glob(f"{filedir}/*.png")
    times = []
    files.sort(key = lambda x: int(x.split("\\")[-1].split("_")[0]))

    first_minute = get_vals(files[0])[1]
    last_frame = 0

    for f in files:
        frame_no, minute, second, millisecond = get_vals(f)
        ttime = float(second + "." + millisecond)
        minute_diff = (int(minute) - int(first_minute))%60
        ttime += minute_diff
        if last_frame != frame_no: # Avoid zeros jic
            ttime = ttime*(int(last_frame) - int(frame_no))
        last_frame = frame_no
        first_minute = minute
        times.append(ttime)

    if len(times) % 2 != 0:
        times = times[1:]

    avg = 0
    ctr = 0
    for i in range(len(times) - 1):
        avg += times[i + 1] - times[i]
        ctr += 1

    print("FPS:", avg*100./ctr)

