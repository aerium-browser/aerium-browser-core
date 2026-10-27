// Copyright 2026 Dioide
// SPDX-License-Identifier: GPL-3.0-only

package com.aeriumbrowser.bridge;

import androidx.annotation.Nullable;

import com.aeriumbrowser.api.AeriumCore;

public final class Aerium {
    private static @Nullable AeriumCore sCore;

    private Aerium() {}

    public static AeriumCore core() {
        if (sCore == null) sCore = new CoreImpl();
        return sCore;
    }
}
