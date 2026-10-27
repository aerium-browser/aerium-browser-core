// Copyright 2026 Dioide
// SPDX-License-Identifier: GPL-3.0-only

package com.aeriumbrowser.api;

public interface SurfaceHost {
    int NO_TAB = -1;

    AeriumCore core();

    int tabId();

    void close();

    void open(Slot slot);

    void showDefault();
}
