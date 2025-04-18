# Copyright 2024 Marimo. All rights reserved.
"""marimo backend for matplotlib

Adapted from

matplotlib/matplotlib/blob/main/lib/matplotlib/backends/backend_template.py

and

https://stackoverflow.com/questions/58153024/matplotlib-how-to-create-original-backend
"""

from __future__ import annotations

import base64
import io
from typing import Optional

import matplotlib.pyplot as plt
from matplotlib._pylab_helpers import Gcf
from matplotlib.backend_bases import (
    FigureCanvasBase,
    FigureManagerBase,
)
from matplotlib.backends.backend_agg import FigureCanvasAgg

from marimo._messaging.cell_output import CellChannel
from marimo._messaging.mimetypes import KnownMimeType
from marimo._messaging.ops import CellOp
from marimo._utils.data_uri import build_data_url

FigureCanvas = FigureCanvasAgg


def close_figures() -> None:
    if Gcf.get_all_fig_managers():
        plt.close("all")


def _internal_show(canvas: FigureCanvasBase) -> None:
    buf = io.BytesIO()
    buf.seek(0)
    canvas.figure.savefig(buf, format="png", bbox_inches="tight")  # type: ignore[attr-defined]
    plt.close(canvas.figure)
    mimetype: KnownMimeType = "image/png"
    plot_bytes = base64.b64encode(buf.getvalue())
    CellOp.broadcast_console_output(
        channel=CellChannel.MEDIA,
        mimetype=mimetype,
        data=build_data_url(mimetype=mimetype, data=plot_bytes),
        cell_id=None,
        status=None,
    )


class FigureManager(FigureManagerBase):
    def show(self) -> None:
        _internal_show(self.canvas)


def show(*, block: Optional[bool] = None) -> None:
    del block
    for manager in Gcf.get_all_fig_managers():
        _internal_show(manager.canvas)
