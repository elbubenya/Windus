"""
Profiler wrapper for main.py

Usage:
    python profile_main.py            # runs main.py under cProfile until Ctrl+C, then prints stats
    python profile_main.py --dump out.prof   # also saves raw stats to a file for snakeviz/tuna etc.

Since main.py runs an infinite `while True` loop, this wrapper catches
KeyboardInterrupt (Ctrl+C) so you can stop it whenever you're done
profiling and still get the report.
"""

import cProfile
import pstats
import io
import os
import runpy
import signal
import sys
import threading
import argparse


def main():
    parser = argparse.ArgumentParser(description="Profile main.py")
    parser.add_argument(
        "--dump",
        metavar="FILE",
        help="Also save raw profiling stats to FILE (e.g. out.prof) for tools like snakeviz/tuna",
    )
    parser.add_argument(
        "--sort",
        default="cumulative",
        choices=["cumulative", "tottime", "calls", "ncalls"],
        help="How to sort the printed stats table (default: cumulative)",
    )
    parser.add_argument(
        "--lines",
        type=int,
        default=40,
        help="How many rows of the stats table to print (default: 40)",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=None,
        metavar="SECONDS",
        help="Auto-stop profiling after this many seconds (in addition to Ctrl+C)",
    )
    parser.add_argument(
        "target",
        nargs="?",
        default="main.py",
        help="Path to the script to profile (default: main.py)",
    )
    args = parser.parse_args()

    profiler = cProfile.Profile()

    timer = None
    if args.duration is not None:
        def _autostop():
            print(f"\n[profiler] {args.duration}s elapsed, auto-stopping...\n")
            # Send SIGINT to ourselves so the same KeyboardInterrupt path
            # used by Ctrl+C handles the stop/report, regardless of what
            # the target script is doing at the time (sleep, keyboard hook, etc.)
            if os.name == "nt":
                signal.raise_signal(signal.SIGINT)
            else:
                os.kill(os.getpid(), signal.SIGINT)

        timer = threading.Timer(args.duration, _autostop)
        timer.daemon = True
        timer.start()

    stop_desc = f"after {args.duration}s or Ctrl+C" if args.duration else "with Ctrl+C"
    print(f"Profiling '{args.target}'. Stop {stop_desc} to see the report.\n")

    try:
        profiler.enable()
        # Runs the target script as if it were invoked directly (as __main__),
        # so its own imports/relative paths behave the same as `python main.py`.
        runpy.run_path(args.target, run_name="__main__")
    except KeyboardInterrupt:
        print("\nStopped. Generating profile report...\n")
    finally:
        if timer is not None:
            timer.cancel()
        profiler.disable()

        if args.dump:
            profiler.dump_stats(args.dump)
            print(f"Raw stats saved to '{args.dump}' "
                  f"(open with: python -m pstats {args.dump}, or snakeviz/tuna)\n")

        stream = io.StringIO()
        stats = pstats.Stats(profiler, stream=stream).sort_stats(args.sort)
        stats.print_stats(args.lines)
        print(stream.getvalue())


if __name__ == "__main__":
    main()