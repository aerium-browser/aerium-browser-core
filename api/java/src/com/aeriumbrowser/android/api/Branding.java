// Copyright 2026 Aerium Browser
// SPDX-License-Identifier: GPL-3.0-only

package com.aeriumbrowser.android.api;

import androidx.annotation.DrawableRes;

public interface Branding {
    String appName();

    @DrawableRes
    int logo();
}
