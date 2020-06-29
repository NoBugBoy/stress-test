#-*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys
import time
import copy
import threading
from collections import deque

try:
    from shutil import get_terminal_size
    def get_terminal_width():
        return get_terminal_size().columns
except ImportError:
    import subprocess
    def get_terminal_width():
        return int(subprocess.check_output(["tput", "cols"]))

_chars = {
    "block": "  ▏▎▍▌▋▊▉█",
    "shades": " ░▒▓█",
    "braille": " ⡀⡄⡆⡇⣇⣧⣷⣿",
    "ascii": " -=#"
}

_spinners = {
    "simple": ("*----", "-*---", "--*--", "---*-",
               "----*", "---*-", "--*--", "-*---"),
    "fish": (">))'>    ", " >))'>   ", "  >))'>  ", "   >))'> ",
             "    <'((<", "   <'((< ", "  <'((<  ", " <'((<   ")
}

_templates = {
    "detailed": "{subject} [{progressbar}] %{percentage:.2f} Elapsed: {seconds:.0f}s ETA: {eta:.0f}s",
    "timer": "{seconds:.0f}s"
}

class Bar(object):
    def __init__(self, subject="", **kwargs):
        object.__setattr__(self, "_args", {
            "subject"           : subject,
            "count"             : kwargs.pop("count", 0),
            "progressbar_width" : kwargs.pop("progressbar_width", -1),
            "end"               : kwargs.pop("end", None)
        })

        chars                  = kwargs.pop("chars", "block")
        self._args["chars"]    = _chars.get(chars, chars)

        template               = kwargs.pop("template", "detailed")
        self._args["template"] = _templates.get(template, template)

        spinner                = kwargs.pop("spinner", "fish")
        self._args["spinner"]  = _spinners.get(spinner, spinner)

        if kwargs:
            raise ValueError("Invalid arguments: " + ", ".join(kwargs))

    def __enter__(self):
        return ActiveBar(**self._args)

    def __exit__(self, *args):
        bar = ActiveBar.pop_last_instance()
        bar.exit()

    def __call__(self, **kwargs):
        d = self._args.copy()
        d.update(kwargs)
        return Bar(**d)

    def map(self, f, *iterables):
        l = sum(len(i) for i in iterables)
        with self(count=l) as b:
            list(b.map(f, *iterables))

    # Make the class immutable
    def __setattr__(self, k, v):
        raise TypeError
    def __delattr__(self, k, v):
        raise TypeError

class ActiveBar(object):
    _instances = []

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

        self._instances.append(self)

        self._stopped = False
        self._timer = None
        self._step = 0
        self._last_step = 0
        self._last_update = 0
        self._started_at = time.time()
        self._max_length = 0

        self._tick()

    @classmethod
    def pop_last_instance(cls):
        return cls._instances.pop()

    def _overwrite(self, line):
        print("\r" + line + ' ' * max(0, self._max_length - len(line)), end="")
        sys.stdout.flush()
        self._max_length = max(self._max_length, len(line))

    def _tick(self):
        self.update_bar()
        self._timer = threading.Timer(1, self._tick)
        self._timer.start()

    def update_bar(self, force=False):
        if self._stopped: return

        now = time.time()
        if now - self._last_update < 0.1 and not force:
            return
        self._last_update = now

        subject = self.subject if self.subject is not None \
                               else self.subject
        step = self._step
        count = self.count
        remaining_steps = count - step
        completed = step / max(count, 0) if count else 0
        percentage = completed * 100
        seconds = now - self._started_at

        seconds_per_step = (self._last_step - self._started_at) / step if step else 0
        eta = max(0, seconds_per_step  * remaining_steps)

        spinner = self.spinner[int(seconds * 2) % len(self.spinner)]

        progressbar = self._create_progressbar(self.progressbar_width) \
                          if self.progressbar_width > 0 \
                          else "{progressbar}"

        line = self.template.format(**locals())

        if self.progressbar_width < 0:
            width = get_terminal_width() - len(line) + len("{progressbar}")
            line = line.format(progressbar=self._create_progressbar(width))

        self._overwrite(line)

    def _create_progressbar(self, width):
        completed = self._step / max(self.count, 0) if self.count else 0

        full_bar_count, rem = divmod(completed * width, 1)
        bar = int(full_bar_count) * self.chars[-1]
        if rem: bar += self.chars[int(rem * len(self.chars))]
        bar = bar[:width]

        empty_count = width - len(bar)
        bar += empty_count * self.chars[0]

        return bar

    def watch(self, f):
        def wrapped(*args, **kwargs):
            f(*args, **kwargs)
            self.step()
        return wrapped

    def map(self, f, *iterables):
        return map(self.watch(f), *iterables)

    def cancel(self):
        self._stop()
        print()

    def exit(self):
        self._stop()
        if self.end:
            seconds = self.seconds = time.time() - self._started_at
            subject = self.subject
            self._overwrite(self.end.format(**locals()))
        print()

    def _stop(self):
        if self._timer is  not None:
            self._timer.cancel()
        self._stopped = True
        self.update_bar(force=True)

    def step(self, count=1):
        self._step += count
        self._last_step = time.time()
        self.update_bar()
