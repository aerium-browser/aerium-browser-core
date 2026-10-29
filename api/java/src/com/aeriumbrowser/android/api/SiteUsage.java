// Copyright 2026 Aerium Browser
// SPDX-License-Identifier: GPL-3.0-only

package com.aeriumbrowser.android.api;

public final class SiteUsage {
    public final int cookies;
    public final long bytes;
    public final int permissions;

    public SiteUsage(int cookies, long bytes, int permissions) {
        this.cookies = cookies;
        this.bytes = bytes;
        this.permissions = permissions;
    }
}
