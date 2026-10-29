// Copyright 2026 Aerium Browser
// SPDX-License-Identifier: GPL-3.0-only

package com.aeriumbrowser.android.bridge;

import com.aeriumbrowser.android.api.ActionsApi;
import com.aeriumbrowser.android.api.AeriumCore;
import com.aeriumbrowser.android.api.BrowsingDataApi;
import com.aeriumbrowser.android.api.ExtensionsApi;
import com.aeriumbrowser.android.api.NavigationApi;
import com.aeriumbrowser.android.api.PrefsApi;
import com.aeriumbrowser.android.api.SettingsApi;
import com.aeriumbrowser.android.api.SitesApi;
import com.aeriumbrowser.android.api.TabsApi;
import com.aeriumbrowser.android.api.WebAppsApi;

import org.chromium.build.annotations.ServiceImpl;

@ServiceImpl(AeriumCore.class)
public class CoreService implements AeriumCore {
    private final AeriumCore mCore = Aerium.core();

    @Override
    public int apiVersion() {
        return mCore.apiVersion();
    }

    @Override
    public SettingsApi settings() {
        return mCore.settings();
    }

    @Override
    public TabsApi tabs() {
        return mCore.tabs();
    }

    @Override
    public NavigationApi navigation() {
        return mCore.navigation();
    }

    @Override
    public BrowsingDataApi browsingData() {
        return mCore.browsingData();
    }

    @Override
    public ExtensionsApi extensions() {
        return mCore.extensions();
    }

    @Override
    public SitesApi sites() {
        return mCore.sites();
    }

    @Override
    public PrefsApi prefs() {
        return mCore.prefs();
    }

    @Override
    public ActionsApi actions() {
        return mCore.actions();
    }

    @Override
    public WebAppsApi webApps() {
        return mCore.webApps();
    }
}
