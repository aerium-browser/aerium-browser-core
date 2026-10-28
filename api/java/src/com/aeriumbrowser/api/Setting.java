// Copyright 2026 Aerium Browser
// SPDX-License-Identifier: GPL-3.0-only

package com.aeriumbrowser.api;

public final class Setting<T> {
    public final String key;
    public final Class<T> type;

    Setting(String key, Class<T> type) {
        this.key = key;
        this.type = type;
    }
}
