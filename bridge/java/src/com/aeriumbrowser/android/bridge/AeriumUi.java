// Copyright 2026 Aerium Browser
// SPDX-License-Identifier: GPL-3.0-only

package com.aeriumbrowser.android.bridge;

import androidx.annotation.Nullable;

import com.aeriumbrowser.android.api.Slot;
import com.aeriumbrowser.android.api.SurfaceFactory;
import com.aeriumbrowser.android.api.UiProvider;

import org.chromium.base.ServiceLoaderUtil;

public final class AeriumUi {
    private static boolean sLoaded;
    private static @Nullable UiProvider sProvider;

    private AeriumUi() {}

    public static @Nullable UiProvider get() {
        if (!sLoaded) {
            sLoaded = true;
            sProvider = ServiceLoaderUtil.maybeCreate(UiProvider.class);
            if (sProvider != null) sProvider.attach(Aerium.core());
        }
        return sProvider;
    }

    public static @Nullable SurfaceFactory surface(Slot slot) {
        UiProvider provider = get();
        return provider == null ? null : provider.surface(slot);
    }
}
