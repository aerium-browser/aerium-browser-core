// Copyright 2026 Dioide
// SPDX-License-Identifier: GPL-3.0-only

package com.aeriumbrowser.api;

import androidx.annotation.Nullable;

public interface MenuHost extends SurfaceHost {
    @Nullable
    MenuItem item(int id);

    void select(int id);

    default boolean overview() {
        return false;
    }
}
