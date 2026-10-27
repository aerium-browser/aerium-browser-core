// Copyright 2026 Dioide
// SPDX-License-Identifier: GPL-3.0-only

package com.aeriumbrowser.bridge;

import android.app.Activity;

import com.aeriumbrowser.api.ActionsApi;

import org.chromium.chrome.browser.app.ChromeActivity;

final class ActionsImpl implements ActionsApi {
    @Override
    public boolean run(Activity activity, int actionId) {
        if (!(activity instanceof ChromeActivity chrome)) return false;
        return chrome.onMenuOrKeyboardAction(actionId, false, null, null);
    }
}
