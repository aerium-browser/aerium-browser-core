// Copyright 2026 Dioide
// SPDX-License-Identifier: GPL-3.0-only

package com.aeriumbrowser.bridge;

import com.aeriumbrowser.api.ActionsApi;
import com.aeriumbrowser.api.AeriumCore;
import com.aeriumbrowser.api.BrowsingDataApi;
import com.aeriumbrowser.api.ExtensionsApi;
import com.aeriumbrowser.api.NavigationApi;
import com.aeriumbrowser.api.PrefsApi;
import com.aeriumbrowser.api.SettingsApi;
import com.aeriumbrowser.api.SitesApi;
import com.aeriumbrowser.api.TabsApi;
import com.aeriumbrowser.api.WebAppsApi;

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
