// Copyright 2026 Aerium Browser
// SPDX-License-Identifier: GPL-3.0-only

package com.aeriumbrowser.android.bridge;

import android.app.Activity;

import com.aeriumbrowser.android.api.ActionsApi;

import org.chromium.chrome.browser.app.ChromeActivity;

final class ActionsImpl implements ActionsApi {
    @Override
    public boolean run(Activity activity, int actionId) {
        if (!(activity instanceof ChromeActivity chrome)) return false;
        return chrome.onMenuOrKeyboardAction(actionId, false, null, null);
    }
}
