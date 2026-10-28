// Copyright 2026 Aerium Browser
// SPDX-License-Identifier: GPL-3.0-only

package com.aeriumbrowser.api;

import android.content.Context;
import android.view.View;

import androidx.annotation.Nullable;

public interface SurfaceFactory {
    @Nullable
    View create(Context context, SurfaceHost host);
}
