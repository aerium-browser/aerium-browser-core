// Copyright 2026 Aerium Browser
// SPDX-License-Identifier: GPL-3.0-only

package com.aeriumbrowser.api;

import androidx.annotation.Nullable;

public interface UiProvider {
    void attach(AeriumCore core);

    @Nullable
    SurfaceFactory surface(Slot slot);

    Branding branding();

    ToolbarSpec toolbar();

    ThemeTokens theme();
}
