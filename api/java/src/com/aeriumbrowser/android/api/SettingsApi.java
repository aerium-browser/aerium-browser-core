// Copyright 2026 Aerium Browser
// SPDX-License-Identifier: GPL-3.0-only

package com.aeriumbrowser.android.api;

public interface SettingsApi {
    <T> T get(Setting<T> setting);

    <T> void set(Setting<T> setting, T value);

    Subscription observe(Setting<?> setting, Runnable onChange);
}
