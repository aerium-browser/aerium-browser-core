// Copyright 2026 Dioide
// SPDX-License-Identifier: GPL-3.0-only

package com.aeriumbrowser.api;

import android.app.Activity;

public interface ActionsApi {
    boolean run(Activity activity, int actionId);
}
